# from langchain_text_splitters import MarkdownHeaderTextSplitter
# # from langchain.docstore.document import Document
# import json
# from pathlib import Path

# def load_files():
#     """Load the three files."""
#     with open(r'utils\data\output\ISLR_1stEd-1-30\ISLR_1stEd-1-30.md', encoding='utf-8') as f:
#         md_content = f.read()
#     with open(r'utils\data\output\ISLR_1stEd-1-30\blocks.json', 'r', encoding='utf-8') as f:
#         blocks = json.load(f)
#     with open(r'utils\data\output\ISLR_1stEd-1-30\ISLR_1stEd-1-30_meta.json', 'r', encoding='utf-8') as f:
#         meta = json.load(f)
#     return md_content, blocks, meta

# def get_page_from_blocks(header_text, blocks):
#     """Map header/content to pageid from blocks.json."""
#     header_lower = header_text.lower()
#     for block in blocks:
#         if 'pageid' in block and 'textlines' in block:
#             block_text = block['textlines'].lower()
#             if any(word in block_text for word in header_lower.split()[:3]):
#                 return block['pageid']
#     return 1  # Default fallback

# def detect_images_in_text(text):
#     """Extract image paths from markdown."""
#     import re
#     img_matches = re.findall(r'!\[.*?\]\((.*?)\)', text)
#     return img_matches[0] if img_matches else None

# def chunk_with_langchain(md_content, blocks):
#     """Use LangChain MarkdownHeaderTextSplitter - NO DUPLICATION!"""
    
#     # Define headers to split upon (H1, H2 primary)
#     headers_to_split_on = [
#         ("#", "header"),      # H1 → header
#         ("##", "subheader"),
#         ("###", "subheader"),
#         ("####", "subheader"),  # H2 → subheader
#     ]
    
#     # Create splitter
#     markdown_splitter = MarkdownHeaderTextSplitter(
#         headers_to_split_on=headers_to_split_on,
#         strip_headers=False  # Keep headers in content
#     )
    
#     # Split MD into hierarchical chunks
#     md_docs = markdown_splitter.split_text(md_content)
    
#     # Convert to structured chunks with metadata
#     chunks = []
#     for doc in md_docs:
#         # Extract metadata
#         metadata = doc.metadata.copy()
        
#         # Map page from blocks.json
#         page = get_page_from_blocks(
#             f"{metadata.get('header', '')} {metadata.get('subheader', '')}",
#             blocks
#         )
        
#         # Detect images in this chunk
#         img_path = detect_images_in_text(doc.page_content)
        
#         chunk = {
#             'text': doc.page_content.strip(),
#             'metadata': {
#                 'header': metadata.get('header'),
#                 'subheader': metadata.get('subheader'),
#                 'page': page,
#                 'chunk_size': len(doc.page_content.split()),  # Word count
#                 'token_estimate': len(doc.page_content) // 4,  # Rough token estimate
#                 'image_path': img_path,
#                 'file_id': 'ISLR_1stEd-1-30',
#                 'file_path': 'ISLR_1stEd-1-30.md',
#                 'source': 'langchain_markdown_splitter'
#             }
#         }
        
#         # Only add non-empty chunks
#         if chunk['text'].strip():
#             chunks.append(chunk)
    
#     return chunks

# # Main execution
# if __name__ == "__main__":
#     print("🔍 Loading files...")
#     md_content, blocks, meta = load_files()
    
#     print("✂️  Chunking with LangChain MarkdownHeaderTextSplitter...")
#     chunks = chunk_with_langchain(md_content, blocks)
    
#     # Save perfect structured output
#     output = {
#         'total_chunks': len(chunks),
#         'avg_chunk_size': sum(c['metadata']['chunk_size'] for c in chunks) / len(chunks),
#         'chunks': chunks,
#         'source_files': {
#             'md': 'ISLR_1stEd-1-30.md',
#             'blocks': 'blocks.json',
#             'meta': 'ISLR_1stEd-1-30_meta.json'
#         }
#     }
    
#     with open('structured_chunks.json', 'w', encoding='utf-8') as f:
#         json.dump(output, f, indent=2, ensure_ascii=False)
    
#     print(f"✅ PERFECT! Created {len(chunks)} chunks - NO DUPLICATION!")
#     print(f"📊 Avg chunk size: {output['avg_chunk_size']:.0f} words")
    
#     print("\n📋 Sample chunks (showing hierarchy preservation):")
#     for i, chunk in enumerate(chunks[:3]):
#         print(f"\n--- Chunk {i+1} ---")
#         print(f"Header: {chunk['metadata']['header']}")
#         print(f"Subheader: {chunk['metadata']['subheader']}")
#         print(f"Page: {chunk['metadata']['page']}")
#         print(f"Text preview: {chunk['text'][:150]}...")
#         print(f"Size: {chunk['metadata']['chunk_size']} words")
    
#     print("\n🚀 Ready for Milvus/LangChain vector DB ingestion!")
