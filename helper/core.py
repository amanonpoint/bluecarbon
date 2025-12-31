# helper/core.py
from typing import Dict, Any, Optional, List
import os
from dotenv import load_dotenv

from helper.llm import LLMClient
from helper.retriver_engine import RetrieverEngine
from helper.tools import build_context, chunks_to_sources
from helper.prep_citation import create_section_html_from_listchunk
from helper.memory import SimpleMemoryManager  # Updated import

load_dotenv()

class RagOrchestrator:
    def __init__(
        self,
        milvus_uri: str = "http://localhost:19530",
        collection_name: str = "knowledge_base_v1",
        embedding_model: str = "all-MiniLM-L12-v2",
        groq_model: str = "llama-3.3-70b-versatile",
        prep_citations_func=create_section_html_from_listchunk,
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
        print(f"retrived context:{context_text}")
        
        # STEP 3: Create enhanced prompt
        if memory_context:
            prompt = f"""{memory_context}# DOCUMENT KNOWLEDGE
{context_text}

# QUESTION
{query}

Answer ONLY if the answer is directly supported by the document knowledge above.

CHUNK CITATION RULES (VERY IMPORTANT):
1. You MUST list the EXACT chunk_id values you used to generate the answer
2. Only include chunk_ids that directly support the answer
3. For EACH used chunk_id, explain WHY it was chosen:
   - Reference the specific heading/subheading or concept
   - Explain why other chunks were not relevant
4. If answer does NOT use document knowledge:
   - citation_required = "no"
   - used_chunk_ids = []
   - chunk_reasoning = {{}}
5. Do NOT invent chunk_ids
6. chunk_id values MUST come from DOCUMENT KNOWLEDGE

JSON ONLY – NO OTHER TEXT

Respond in this EXACT JSON format:
{{
  "answer": "Your answer here",
  "citation_required": "yes" or "no",
  "used_chunk_ids": [],
  "chunk_reasoning": {{
    "chunk_id": "Why this chunk supports the answer (mention heading/subheading)"
  }}
}}"""


        else:
            prompt = f"""{memory_context}# DOCUMENT KNOWLEDGE
{context_text}

# QUESTION
{query}

Answer ONLY if the answer is directly supported by the document knowledge above.

CHUNK CITATION RULES (VERY IMPORTANT):
1. You MUST list the EXACT chunk_id values you used to generate the answer
2. Only include chunk_ids that directly support the answer
3. For EACH used chunk_id, explain WHY it was chosen:
   - Reference the specific heading/subheading or concept
   - Explain why other chunks were not relevant
4. If answer does NOT use document knowledge:
   - citation_required = "no"
   - used_chunk_ids = []
   - chunk_reasoning = {{}}
5. Do NOT invent chunk_ids
6. chunk_id values MUST come from DOCUMENT KNOWLEDGE

JSON ONLY – NO OTHER TEXT

Respond in this EXACT JSON format:
{{
  "answer": "Your answer here",
  "citation_required": "yes" or "no",
  "used_chunk_ids": [],
  "chunk_reasoning": {{
    "chunk_id": "Why this chunk supports the answer (mention heading/subheading)"
  }}
}}"""


        
        # STEP 4: Generate response
        llm_response = self.llm_client.generate_json_response(prompt)
        print(f"raw LLM response:\n{llm_response}")
        
        answer = llm_response.get("answer", "No answer generated")
        used_chunk_ids = llm_response.get("used_chunk_ids", [])
        citation_required = (
            llm_response.get("citation_required") == "yes"
            and len(used_chunk_ids) > 0
        )

        citations = []

        if citation_required:
            try:
                # THIS USES YOUR UPDATED FUNCTION
                html_paths = create_section_html_from_listchunk(used_chunk_ids)

                for cid, path in zip(used_chunk_ids, html_paths):
                    citations.append({
                        "chunk_id": cid,
                        "citation_path": path
                    })

            except Exception as e:
                print(f"⚠ Citation generation failed: {e}")

        
        # STEP 6: Update memory
        if session_id:
            await self.memory_manager.add_to_memory(
                session_id=session_id,
                user_message=query,
                ai_response=answer,
                metadata={
                    "citation_required": citation_required,
                    # "citation_limit": citation_limit,
                    # "files_used": files_used,
                    "citations_count": len(citations),
                    "chunks_retrieved": len(chunks)
                }
            )
        
        return {
            "status": "success",
            "query": query,
            "answer": answer,
            "citation_required": citation_required,
            # "citation_limit": citation_limit,
            # "files_used": files_used,
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