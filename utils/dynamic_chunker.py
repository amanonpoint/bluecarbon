from langchain_text_splitters import MarkdownHeaderTextSplitter
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import os
import uuid
import re
from dotenv import load_dotenv

load_dotenv()

JSON_FILE = os.getenv("CHUNK_JSON_FILE")

class DynamicMarkdownChunker:
    """
    Dynamic chunker for marker-generated document folders.
    Handles multiple folder structures each containing:
    - markdown files (.md)
    - JSON metadata (blocks.json, *_meta.json)
    - Image files (.jpg, .png, etc.)
    """
    
    def __init__(self, base_folder_path: str):
        """
        Initialize chunker with base folder path.
        
        Args:
            base_folder_path: Path to parent folder containing marker-generated subfolders
        """
        self.base_path = Path(base_folder_path)
        
        if not self.base_path.exists():
            raise ValueError(f"❌ Base folder not found: {base_folder_path}")
        
        self.base_path = self.base_path.resolve()
        print(f"✅ Base folder set to: {self.base_path}")
    
    def discover_document_folders(self) -> List[Path]:
        """
        Discover all marker-generated document folders.
        Looks for folders containing .md files and .json metadata.
        
        Returns:
            List of valid document folder paths
        """
        doc_folders = []
        
        for item in self.base_path.iterdir():
            if item.is_dir():
                # Check if folder contains marker-generated files
                has_md = list(item.glob('*.md'))
                has_json = list(item.glob('*.json'))
                
                if has_md and has_json:
                    doc_folders.append(item)
                    print(f"  ✓ Found: {item.name}")
        
        if not doc_folders:
            raise ValueError(
                f"❌ No marker-generated folders found in {self.base_path}\n"
                f"Expected folders with .md and .json files"
            )
        
        return sorted(doc_folders)
    
    def load_folder_files(self, folder_path: Path) -> Tuple[str, Dict, Dict, Path]:
        """
        Load markdown, blocks.json, and metadata from a folder.
        
        Args:
            folder_path: Path to the document folder
            
        Returns:
            Tuple of (md_content, blocks, meta, folder_path)
        """
        folder_path = Path(folder_path)
        
        # Find .md file
        md_files = list(folder_path.glob('*.md'))
        if not md_files:
            raise FileNotFoundError(f"❌ No .md file found in {folder_path}")
        md_file = md_files[0]
        
        # Find blocks.json
        blocks_file = folder_path / 'blocks.json'
        if not blocks_file.exists():
            raise FileNotFoundError(f"❌ blocks.json not found in {folder_path}")
        
        # Find *_meta.json
        meta_files = list(folder_path.glob('*_meta.json'))
        if not meta_files:
            raise FileNotFoundError(f"❌ No *_meta.json file found in {folder_path}")
        meta_file = meta_files[0]
        
        # Load files
        try:
            with open(md_file, encoding='utf-8') as f:
                md_content = f.read()
            with open(blocks_file, 'r', encoding='utf-8') as f:
                blocks = json.load(f)
            with open(meta_file, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            
            print(f"  📄 Loaded: {md_file.name}")
            print(f"  📋 Loaded: blocks.json, {meta_file.name}")
            
            return md_content, blocks, meta, folder_path
        
        except Exception as e:
            raise RuntimeError(f"❌ Error loading files from {folder_path}: {e}")
    
    def get_page_range_from_content(self, chunk_text: str, md_content: str) -> str:
        """
        Extract page range from markdown content based on chunk position.
        Searches for {page_no}---- pattern before and after the chunk.
        
        Args:
            chunk_text: The text content of the chunk
            md_content: Full markdown content
            
        Returns:
            Page range as string (e.g., "0", "1", "2-3", "5-7")
        """
        # Clean chunk text for better matching (first 200 chars)
        chunk_sample = chunk_text[:200].strip() if len(chunk_text) > 200 else chunk_text.strip()
        
        # Find the position of chunk text in markdown
        chunk_start = md_content.find(chunk_sample)
        
        # If not found, try without leading/trailing whitespace variations
        if chunk_start == -1:
            # Try to find a smaller unique portion
            lines = chunk_text.split('\n')
            for line in lines[:5]:  # Try first 5 lines
                line_clean = line.strip()
                if len(line_clean) > 20:  # Only use substantial lines
                    chunk_start = md_content.find(line_clean)
                    if chunk_start != -1:
                        break
        
        if chunk_start == -1:
            return "0"
        
        # Get text before chunk to find start page
        text_before = md_content[:chunk_start]
        
        # Find all page markers before chunk: {page_no}----
        page_pattern = r'\{(\d+)\}-+'
        pages_before = re.findall(page_pattern, text_before)
        
        # Start page is the last page marker before chunk, or 0 if none
        start_page = int(pages_before[-1]) if pages_before else 0
        
        # Get text for chunk to find end page
        chunk_end = chunk_start + len(chunk_text)
        text_in_chunk = md_content[chunk_start:chunk_end]
        
        # Find all page markers within chunk
        pages_in_chunk = re.findall(page_pattern, text_in_chunk)
        
        if pages_in_chunk:
            # If chunk contains page markers, end page is the last one found
            end_page = int(pages_in_chunk[-1])
        else:
            # If no page markers in chunk, use start page
            end_page = start_page
        
        # Format page range
        if start_page == end_page:
            return str(start_page)
        else:
            return f"{start_page}-{end_page}"
    
    def find_images_in_folder(self, folder_path: Path) -> Dict[str, Path]:
        """
        Find all image files in the folder.
        
        Args:
            folder_path: Path to document folder
            
        Returns:
            Dict mapping image names to their full paths
        """
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        images = {}
        
        for img_file in folder_path.iterdir():
            if img_file.suffix.lower() in image_extensions:
                images[img_file.name] = img_file
        
        return images
    
    def extract_images_from_markdown(self, text: str) -> List[str]:
        """
        Extract image references from markdown.
        
        Args:
            text: Markdown content
            
        Returns:
            List of image paths referenced in markdown
        """
        img_matches = re.findall(r'!\[.*?\]\((.*?)\)', text)
        return img_matches
    
    def resolve_image_paths(
        self,
        chunk_img_paths: List[str],
        folder_path: Path,
        available_images: Dict[str, Path]
    ) -> Dict[str, Optional[str]]:
        """
        Resolve chunk image paths to actual filesystem paths.
        
        Args:
            chunk_img_paths: Image paths found in markdown
            folder_path: Document folder path
            available_images: Available image files in folder
            
        Returns:
            Dict with chunk_img_path and relative_img_path (as full absolute path)
        """
        result = {
            'chunk_img_path': None,
            'relative_img_path': None
        }
        
        if not chunk_img_paths:
            return result
        
        # Use first image reference
        chunk_img_path = chunk_img_paths[0]
        result['chunk_img_path'] = chunk_img_path
        
        # Extract filename from path (handle various formats)
        img_filename = Path(chunk_img_path).name
        
        # Find matching actual image file
        if img_filename in available_images:
            actual_img_path = available_images[img_filename]
            # Use full absolute path
            result['relative_img_path'] = str(actual_img_path.resolve())
        
        return result
    
    def chunk_folder(self, folder_path: Path) -> Tuple[List[Dict], Dict]:
        """
        Process a single folder: load, chunk, and enrich with metadata.
        
        Args:
            folder_path: Path to document folder
            
        Returns:
            Tuple of (chunks, folder_metadata)
        """
        print(f"\n📂 Processing: {folder_path.name}")
        
        # Load files
        md_content, blocks, meta, _ = self.load_folder_files(folder_path)
        file_id = 'fi_' + str(uuid.uuid4())
        
        # Discover images
        available_images = self.find_images_in_folder(folder_path)
        print(f"  🖼️  Found {len(available_images)} images")
        
        # Define headers for LangChain splitter
        headers_to_split_on = [
            ("#", "header"),
            ("##", "subheader"),
            ("###", "subheader"),
            ("####", "subheader"),
        ]
        
        # Create splitter
        markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split_on,
            strip_headers=False
        )
        
        # Split markdown
        md_docs = markdown_splitter.split_text(md_content)
        print(f"  ✂️  Split into {len(md_docs)} chunks")
        
        # Get the .md file path
        md_file_path = list(folder_path.glob('*.md'))[0]
        
        # Process chunks
        chunks = []
        for doc in md_docs:
            metadata = doc.metadata.copy()
            
            # Get page range from content
            page_range = self.get_page_range_from_content(doc.page_content, md_content)
            
            # Extract and resolve image paths
            chunk_img_paths = self.extract_images_from_markdown(doc.page_content)
            image_data = self.resolve_image_paths(
                chunk_img_paths,
                folder_path,
                available_images
            )
            
            chunk = {
                'text': doc.page_content.strip(),
                'metadata': {
                    'header': metadata.get('header'),
                    'subheader': metadata.get('subheader'),
                    'page': page_range,  # Now returns range like "1", "2-3", etc.
                    'chunk_id': 'chk_' + str(uuid.uuid4()),
                    'chunk_size': len(doc.page_content.split()),  # Word count
                    'chunk_img_path': image_data['chunk_img_path'],  # Markdown reference
                    'relative_img_path': image_data['relative_img_path'],  # Full absolute path
                    'file_id': file_id,  # Generate UUID for each chunk
                    'file_path': str(md_file_path.resolve()),  # Full absolute path to .md file
                    'folder_path': str(folder_path.resolve()),  # Full absolute path to folder
                    'source': 'langchain_markdown_splitter'
                }
            }
            
            if chunk['text'].strip():
                chunks.append(chunk)
        
        # Prepare folder metadata
        folder_metadata = {
            'folder_name': folder_path.name,
            'folder_path': str(folder_path.resolve()),  # Full absolute path
            'total_chunks': len(chunks),
            'avg_chunk_size': sum(c['metadata']['chunk_size'] for c in chunks) / len(chunks) if chunks else 0,
            'total_images': len(available_images),
            'metadata': meta
        }
        
        return chunks, folder_metadata
    
    def process_all_folders(self, output_file: str = JSON_FILE) -> Dict:
        """
        Process all discovered folders and create consolidated output.
        
        Args:
            output_file: Output JSON file path
            
        Returns:
            Complete output dictionary
        """
        print(f"\n🔍 Discovering folders in {self.base_path.name}...")
        doc_folders = self.discover_document_folders()
        print(f"✅ Found {len(doc_folders)} document folders\n")
        
        all_chunks = []
        folders_metadata = []
        
        for folder in doc_folders:
            try:
                chunks, folder_meta = self.chunk_folder(folder)
                all_chunks.extend(chunks)
                folders_metadata.append(folder_meta)
            except Exception as e:
                print(f"  ⚠️  Error processing {folder.name}: {e}")
                continue
        
        # Create consolidated output
        output = {
            'chunks': all_chunks
        }
        
        # Save output
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ SUCCESS! Created {len(all_chunks)} chunks from {len(doc_folders)} folders")
        print(f"💾 Saved to: {output_file}\n")
        
        self._print_sample_chunks(all_chunks)
        
        return output
    
    def _print_sample_chunks(self, chunks: List[Dict], num_samples: int = 3):
        """Print sample chunks for verification."""
        print(f"📋 Sample chunks (showing hierarchy preservation):")
        for i, chunk in enumerate(chunks[:num_samples]):
            print(f"\n--- Chunk {i+1} ---")
            print(f"Chunk ID: {chunk['metadata']['chunk_id']}")
            print(f"File ID: {chunk['metadata']['file_id']}")
            print(f"Folder: {Path(chunk['metadata']['folder_path']).name}")
            print(f"Header: {chunk['metadata']['header']}")
            print(f"Subheader: {chunk['metadata']['subheader']}")
            print(f"Page Range: {chunk['metadata']['page']}")
            print(f"Chunk img path: {chunk['metadata']['chunk_img_path']}")
            print(f"Text preview: {chunk['text'][:150]}...")
            print(f"Size: {chunk['metadata']['chunk_size']} words")
        
        print("\n🚀 Ready for Milvus/LangChain vector DB ingestion!")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    import sys
    
    # Get base folder from command line or use default
    if len(sys.argv) > 1:
        base_folder = sys.argv[1]
    else:
        base_folder = r"utils\data\output"
    
    try:
        # Initialize and process
        chunker = DynamicMarkdownChunker(base_folder)
        output = chunker.process_all_folders()
        
    except ValueError as e:
        print(f"\n❌ {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)