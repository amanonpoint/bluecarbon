# test_retriever_engine.py
import json 
from helper.retriver_engine import RetrieverEngine


def main():
    # Initialize retriever
    retriever = RetrieverEngine(
        milvus_uri="http://localhost:19530",
        collection_name="knowledge_base_v1",
        embedding_model="all-MiniLM-L12-v2",
    )

    # Test queries
    query = "Summarize regression and its types"

    context = retriever.get_retrieval_context(query, limit=10)
    chunks = context["chunks"]
    print(context)

    output_file = "test_retrive.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(context, f, ensure_ascii=False, indent=2)

    print("saved json file!!")

    # print(f"Primary chunks retrieved: {context['primary_chunks_count']}")
    # print()

    # for i, chunk in enumerate(chunks, start=1):
    #     metadata = chunk["metadata"]

    #     print(f"[{i}] ID: {chunk['id']}")
    #     print(f"    Distance     : {chunk['distance']:.4f}")
    #     print(f"    File ID      : {metadata.get('file_id')}")
    #     print(f"    Header       : {metadata.get('header')}")
    #     print(f"    Subheader    : {metadata.get('subheader')}")
    #     print(f"    Page         : {metadata.get('page')}")
    #     print(f"    Chunk ID     : {metadata.get('chunk_id')}")
    #     print(f"    Chunk Size   : {metadata.get('chunk_size')}")
    #     print("    Text Preview :")
    #     print(f"    {chunk['text'][:300]}")  # first 300 chars
    #     print()

    # print("=" * 80)
    # print("Retriever test completed successfully.")


if __name__ == "__main__":
    main()
