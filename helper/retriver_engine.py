# helper/retriver_engine.py
from __future__ import annotations

from typing import List, Dict, Any, Optional

from pymilvus import connections, Collection
from langchain_huggingface import HuggingFaceEmbeddings  # ← ye use karo



class RetrieverEngine:
    def __init__(
        self,
        milvus_uri: str = "http://localhost:19530",
        collection_name: str = "knowledge_base_v1",
        embedding_model: str = "all-MiniLM-L12-v2",
    ):
        # LangChain HF Embeddings (384 dim)
        self.embedding_model = HuggingFaceEmbeddings(
            model_name=embedding_model
        )
        
        # Milvus connection
        from pymilvus import connections, Collection
        connections.connect(alias="default", host='localhost', port='19530')
        self.collection = Collection(collection_name)
        self.collection.load()

    # ---- public API ----
    def get_retrieval_context(self, query: str, limit: int = 10):
        primary = self.search_similar_chunks(query, limit=limit)  # Pass limit
        return {
            "chunks": primary,
            "primary_chunks_count": len(primary),
            "total_chunks_retrieved": len(primary),
        }

    # ---- internal ----
    def _embed_query(self, text: str) -> List[float]:
        vec = self.embedder.encode(text)
        return vec.tolist()


    def search_similar_chunks(self, query: str, limit: int = 10):
        query_embedding = self.embedding_model.embed_query(query)
        
        results = self.collection.search(
            data=[query_embedding],
            anns_field="vector",
            param={"params": {"nprobe": 10}},
            limit=limit,  # ✅ Dynamic limit
            output_fields=["text", "header", "subheader", "page", "chunk_id", "file_id", "chunk_size"]
        )
        
        chunks = []
        for hits in results:
            for hit in hits:
                chunks.append({
                    "id": hit.id,
                    "distance": hit.distance,
                    "text": hit.entity.get("text", ""),
                    "metadata": {
                        "header": hit.entity.get("header", ""),
                        "subheader": hit.entity.get("subheader", ""),
                        "page": hit.entity.get("page", ""),
                        "chunk_id": hit.entity.get("chunk_id", ""),
                        "file_id": hit.entity.get("file_id", ""),
                        "chunk_size": hit.entity.get("chunk_size", 0),
                    }
                })
        return chunks



    def _augment_by_header(self, primary: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Fetch more chunks with same file_id+header as top hit."""
        if not primary:
            return []

        top = primary[0]["metadata"]
        file_id = top.get("file_id")
        header = top.get("header")

        expr_parts = []
        if file_id:
            expr_parts.append(f'metadata["file_id"] == "{file_id}"')
        if header:
            expr_parts.append(f'metadata["header"] == "{header}"')
        if not expr_parts:
            return primary

        expr = " and ".join(expr_parts)

        extra = self.collection.query(
            expr=expr,
            output_fields=["text", "metadata"],
            limit=20,
        )

        existing_ids = {
            c["metadata"].get("chunk_id") for c in primary if c["metadata"].get("chunk_id")
        }
        for e in extra:
            md = e.get("metadata", {})
            if md.get("chunk_id") in existing_ids:
                continue
            primary.append(
                {
                    "text": e.get("text", ""),
                    "metadata": md,
                    "similarity_score": 0.0,  # treat as context, not ranked
                }
            )

        return primary
    
    # helper/retriver_engine.py ke andar
    def get_chunks_for_query(self, query: str):
        """Legacy method for tools"""
        ctx = self.get_retrieval_context(query)
        return ctx["chunks"]


