# helper/core.py
from typing import Dict, Any, Optional, List
import os
from dotenv import load_dotenv

from helper.llm import LLMClient
from helper.retriver_engine import RetrieverEngine
from helper.tools import build_context, chunks_to_sources
from helper.prep_citation import create_section_html_from_chunk
from helper.memory import SimpleMemoryManager  # Updated import

load_dotenv()

class RagOrchestrator:
    def __init__(
        self,
        milvus_uri: str = "http://localhost:19530",
        collection_name: str = "knowledge_base_v1",
        embedding_model: str = "all-MiniLM-L12-v2",
        groq_model: str = "llama-3.3-70b-versatile",
        prep_citations_func=create_section_html_from_chunk,
    ):
        self.llm_client = LLMClient(groq_model)
        self.retriever = RetrieverEngine(
            milvus_uri=milvus_uri,
            collection_name=collection_name,
            embedding_model=embedding_model,
        )
        self.memory_manager = SimpleMemoryManager()  # Simple memory manager
        self.prep_citations_func = prep_citations_func
    
    async def process_query(
        self, 
        query: str, 
        session_id: Optional[str] = None, 
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        
        # STEP 1: Get memory context if session exists
        memory_context = ""
        if session_id:
            memory_context = await self.memory_manager.get_memory_context(session_id, query)
        
        # STEP 2: Retrieve relevant documents
        retrieval = self.retriever.get_retrieval_context(query)
        chunks = retrieval["chunks"]
        context_text = build_context(chunks)
        
        # STEP 3: Create enhanced prompt
        if memory_context:
            prompt = f"""{memory_context}# DOCUMENT KNOWLEDGE
{context_text}

# CURRENT QUESTION
{query}

Answer based on both conversation history and document knowledge above.
Be consistent with previous discussions.

SMART CITATION RULES:
# 1. Answer ONLY if query is DIRECTLY in context
# 2. Count UNIQUE file_id's in context:
#    - 1 file → "files_used": 1, "citation_limit": 1
#    - 2 files → "files_used": 2, "citation_limit": 2  
#    - 3+ files → "files_used": 3, "citation_limit": 3
# 3. Same file multiple chunks → count as 1 file
# 4. citation_required: "yes" ONLY if answer uses context

# JSON ONLY - NO OTHER TEXT!

Respond in this exact JSON format:
{{
  "answer": "Your detailed answer here...",
  "citation_required": "yes" or "no",
  "citation_limit": 0,
  "files_used": 0
}}"""
        else:
            prompt = f"""# DOCUMENT KNOWLEDGE
{context_text}

# QUESTION
{query}

Answer based on the document knowledge above.

SMART CITATION RULES:
# 1. Answer ONLY if query is DIRECTLY in context
# 2. Count UNIQUE file_id's in context:
#    - 1 file → "files_used": 1, "citation_limit": 1
#    - 2 files → "files_used": 2, "citation_limit": 2  
#    - 3+ files → "files_used": 3, "citation_limit": 3
# 3. Same file multiple chunks → count as 1 file
# 4. citation_required: "yes" ONLY if answer uses context

# JSON ONLY - NO OTHER TEXT!

Respond in this exact JSON format:
{{
  "answer": "Your detailed answer here...",
  "citation_required": "yes" or "no",
  "citation_limit": 0,
  "files_used": 0
}}"""
        
        # STEP 4: Generate response
        llm_response = self.llm_client.generate_json_response(prompt)
        
        answer = llm_response.get("answer", "No answer generated")
        citation_required = llm_response.get("citation_required", "no") == "yes"
        citation_limit = int(llm_response.get("citation_limit", 0))
        files_used = int(llm_response.get("files_used", 0))
        
        # STEP 5: Citations
        citations = []
        if citation_required and citation_limit > 0:
            try:
                citation_retrieval = self.retriever.get_retrieval_context(
                    query,
                    limit=citation_limit
                )
                citation_chunks = citation_retrieval["chunks"]
                sources = chunks_to_sources(citation_chunks)
                citations = self._prepare_citations(sources)
            except Exception as e:
                print(f"⚠ Citation error: {e}")
        
        # STEP 6: Update memory
        if session_id:
            await self.memory_manager.add_to_memory(
                session_id=session_id,
                user_message=query,
                ai_response=answer,
                metadata={
                    "citation_required": citation_required,
                    "citation_limit": citation_limit,
                    "files_used": files_used,
                    "citations_count": len(citations),
                    "chunks_retrieved": len(chunks)
                }
            )
        
        return {
            "status": "success",
            "query": query,
            "answer": answer,
            "citation_required": citation_required,
            "citation_limit": citation_limit,
            "files_used": files_used,
            "citations": citations,
            "chunks_retrieved": len(chunks),
            "session_id": session_id,
            "memory_used": bool(memory_context)
        }
    
    def _prepare_citations(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prepare citations from sources"""
        out = []
        for s in sources:
            file_id = s.get("file_id")
            chunk_id = s.get("chunk_id")
            if file_id and chunk_id:
                try:
                    html_path = self.prep_citations_func(file_id, chunk_id)
                    out.append({**s, "citation_path": html_path})
                except Exception:
                    out.append({**s, "citation_path": None})
        return out
    
    async def get_memory_info(self, session_id: str) -> Dict[str, Any]:
        """Get memory information"""
        return self.memory_manager.get_session_info(session_id)