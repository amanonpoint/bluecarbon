import json
import os
from typing import List, Set
from dotenv import load_dotenv

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_milvus import Milvus
from langchain_core.documents import Document

# Load environment variables from .env file
load_dotenv()

# --- Configuration from Environment Variables ---
JSON_FILE = os.getenv("CHUNK_JSON_FILE", "structured_chunks.json")
LOG_FILE = os.getenv("INGESTION_LOG_FILE", "ingestion_log.json")
MILVUS_URI = os.getenv("MILVUS_URI", "http://localhost:19530")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "knowledge_base_v1")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L12-v2")

print("Configuration loaded:")
print(f"JSON_FILE: {JSON_FILE}")
print(f"LOG_FILE: {LOG_FILE}")
print(f"MILVUS_URI: {MILVUS_URI}")
print(f"COLLECTION_NAME: {COLLECTION_NAME}")
print(f"EMBEDDING_MODEL: {EMBEDDING_MODEL}")

def load_processed_ids() -> Set[str]:
    """Load the set of already processed chunk IDs from the log file."""
    if not os.path.exists(LOG_FILE):
        return set()
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return set(data.get("processed_chunk_ids", []))
    except json.JSONDecodeError:
        return set()

def save_processed_ids(new_ids: Set[str]):
    """Update the log file with newly processed IDs."""
    existing_ids = load_processed_ids()
    updated_ids = existing_ids.union(new_ids)
    
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump({"processed_chunk_ids": list(updated_ids)}, f, indent=2)

def clean_metadata(metadata: dict) -> dict:
    """
    Clean metadata to ensure compatibility with Milvus.
    - Converts None values to empty strings (Milvus doesn't like None for string fields).
    - Ensures all values are simple types (str, int, float, bool).
    """
    clean = {}
    for k, v in metadata.items():
        if v is None:
            clean[k] = ""
        elif isinstance(v, (str, int, float, bool)):
            clean[k] = v
        else:
            # Convert lists/dicts to string representation if necessary
            clean[k] = str(v)
    return clean

def main():
    # 1. Load Data
    print(f"Loading data from {JSON_FILE}...")
    try:
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            chunks = data.get("chunks", [])
    except FileNotFoundError:
        print(f"Error: {JSON_FILE} not found.")
        return

    # 2. Filter Processed Chunks
    processed_ids = load_processed_ids()
    documents_to_ingest = []
    new_chunk_ids = set()

    print(f"Found {len(chunks)} total chunks. Checking log for duplicates...")

    for chunk in chunks:
        # Extract ID and Text
        meta = chunk.get("metadata", {})
        chunk_id = meta.get("chunk_id")
        text_content = chunk.get("text")

        if not chunk_id or not text_content:
            continue  # Skip invalid chunks

        # Skip if already in log
        if chunk_id in processed_ids:
            continue

        # Prepare Document for LangChain
        # We clean metadata to avoid 'NoneType' errors in Milvus
        clean_meta = clean_metadata(meta)
        
        doc = Document(
            page_content=text_content,
            metadata=clean_meta
        )
        documents_to_ingest.append(doc)
        new_chunk_ids.add(chunk_id)

    if not documents_to_ingest:
        print("All chunks have already been ingested. Nothing to do.")
        return

    print(f"Preparing to ingest {len(documents_to_ingest)} new chunks...")

    # 3. Initialize Embeddings & Vector Store
    print(f"Initializing embedding model ({EMBEDDING_MODEL})...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    print(f"Connecting to Milvus at {MILVUS_URI}...")
    vector_store = Milvus(
        embedding_function=embeddings,
        connection_args={"uri": MILVUS_URI},
        collection_name=COLLECTION_NAME,
        auto_id=True,  # Milvus will generate primary keys, we store chunk_id in metadata
        drop_old=False # Important: Append to existing collection, don't delete it
    )

    # 4. Ingest Data
    # We ingest in batches to be safe, though LangChain handles this well
    try:
        print("Ingesting documents into Milvus...")
        vector_store.add_documents(documents_to_ingest)
        print("Ingestion complete!")

        # 5. Update Log File
        print("Updating log file...")
        save_processed_ids(new_chunk_ids)
        print(f"Successfully logged {len(new_chunk_ids)} new chunks to {LOG_FILE}.")

    except Exception as e:
        print(f"An error occurred during ingestion: {e}")

if __name__ == "__main__":
    main()
