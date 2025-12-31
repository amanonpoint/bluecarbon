from __future__ import annotations
from typing import List, Dict, Any
from langchain.tools import tool


def build_context(chunks):
    """
    Build LLM context with explicit file + chunk grounding.
    """
    from collections import defaultdict

    files = defaultdict(list)

    for c in chunks:
        md = c.get("metadata", {})
        file_id = md.get("file_id", "unknown_file")
        files[file_id].append(c)

    parts = []

    for file_id, file_chunks in files.items():
        parts.append(f"\n=== FILE: {file_id} ===\n")

        for c in file_chunks:
            md = c.get("metadata", {})
            chunk_id = md.get("chunk_id", "unknown_chunk")
            header = md.get("header", "")
            subheader = md.get("subheader", "")
            page = md.get("page", "")

            heading = " → ".join(
                h for h in [header, subheader] if h
            )

            parts.append(
                f"""[chunk_id: {chunk_id}]
[page: {page} | {heading}]
{c.get("text", "")}
"""
            )

    return "\n---\n".join(parts)




def chunks_to_sources(chunks):
    return [
        {
            "file_id": c["metadata"].get("file_id"),
            "chunk_id": c["metadata"].get("chunk_id"),
            "page": c["metadata"].get("page"),
            "header": c["metadata"].get("header") or c["metadata"].get("subheader"),
        }
        for c in chunks
    ]



# ---------------- LangChain tools for custom agent -----------------

# Note: in clean architecture, retriever Milvus call core.py me hota hai,
# isliye yahan RETRIEVER_FN hata diya; ye tools sirf string/context operate karte.


@tool("summarize_context", return_direct=False)
def summarize_context(context: str) -> str:
    """
    Take long textbook context and produce a concise summary
    (max ~200 words). Use when user explicitly asks for summary /
    overview / high-level explanation.
    Input: raw context text.
    Output: natural-language summary for the user.
    """
    # Actual summarization LLM prompt agent/system prompt se handle karega.
    # Tool ka kaam sirf yeh batana hai ki "summary chahiye".
    return f"SUMMARY_NEEDED\n{context}"


@tool("define_from_context", return_direct=False)
def define_from_context(term_and_context: str) -> str:
    """
    Explain a technical term using ONLY the given context.
    Input format: 'TERM\\n\\nCONTEXT...'.
    Output: natural-language definition + intuition.
    """
    return f"DEFINE_TERM\n{term_and_context}"


@tool("qa_from_context", return_direct=False)
def qa_from_context(question_and_context: str) -> str:
    """
    Answer a user's question using ONLY the given context.
    Input format: 'QUESTION\\n\\nCONTEXT...'.
    Output: natural-language answer.
    """
    return f"QA_NEEDED\n{question_and_context}"
