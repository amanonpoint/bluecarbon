import re
import os
from pymilvus import connections, Collection
import pypandoc

# =========================
# CONFIG
# =========================

MILVUS_URI = "http://localhost:19530"
COLLECTION_NAME = "knowledge_base_v1"

# =========================
# HELPER: ESCAPE MILVUS STRING
# =========================

def resolve_file_ids_for_chunks(chunk_ids):
    connections.connect(uri=MILVUS_URI)
    col = Collection(COLLECTION_NAME)
    col.load()

    # Build: "chk1","chk2","chk3"
    chunk_id_list = ",".join([f'"{c}"' for c in chunk_ids])

    results = col.query(
        expr=f"chunk_id in [{chunk_id_list}]",
        output_fields=["chunk_id", "file_id"],
        limit=1000
    )

    grouped = {}
    for r in results:
        grouped.setdefault(r["file_id"], []).append(r["chunk_id"])

    return grouped


def escape_milvus_string(value: str) -> str:
    """
    Escape special characters for Milvus query expressions.
    Milvus uses double quotes for strings, so we need to escape:
    - Backslashes (\)
    - Double quotes (")
    """
    # Escape backslashes first (must be done before escaping quotes)
    value = value.replace("\\", "\\\\")
    # Escape double quotes
    value = value.replace('"', '\\"')
    return value

# =========================
# MILVUS
# =========================

def fetch_all_chunks(file_id):
    connections.connect(uri=MILVUS_URI)
    col = Collection(COLLECTION_NAME)
    col.load()
    
    # Escape file_id (though it's usually safe)
    file_id_escaped = escape_milvus_string(file_id)
    
    return col.query(
        expr=f'file_id == "{file_id_escaped}"',
        output_fields=[
            "chunk_id",
            "text",
            "page",
            "header",
            "relative_img_path"
        ],
        limit=10000
    )


def fetch_chunks_by_header(file_id, header):
    """
    Fetch chunks by file_id and header.
    Headers may contain special characters like <, >, *, ", etc.
    """
    connections.connect(uri=MILVUS_URI)
    col = Collection(COLLECTION_NAME)
    col.load()
    
    # Escape both file_id and header
    file_id_escaped = escape_milvus_string(file_id)
    header_escaped = escape_milvus_string(header)
    
    try:
        return col.query(
            expr=f'file_id == "{file_id_escaped}" && header == "{header_escaped}"',
            output_fields=[
                "chunk_id",
                "text",
                "page",
                "header",
                "relative_img_path"
            ],
            limit=10000
        )
    except Exception as e:
        print(f"Error querying Milvus with header: {header}")
        print(f"Error: {e}")
        # Fallback: fetch all chunks for this file and filter in Python
        print("   Falling back to Python filtering...")
        all_chunks = fetch_all_chunks(file_id)
        return [c for c in all_chunks if c.get("header") == header]

# =========================
# HEADING
# =========================

def detect_heading(chunk):
    if chunk.get("header"):
        return chunk["header"].strip()

    m = re.search(r"^(\d+(?:\.\d+)*)\s+(.*)$", chunk["text"], re.MULTILINE)
    if m:
        return m.group(2).strip()

    # raise ValueError("Heading not found")
    return "Referenced Section"

# =========================
# MARKDOWN BUILDER
# =========================

def build_section_markdown(chunks, target_chunk_id, heading):
    md = []
    md.append(f"# {heading}\n")

    last_page = None

    for c in sorted(chunks, key=lambda x: x["chunk_id"]):
        page_meta = c["page"]

        # logical page break when metadata page changes
        if last_page and page_meta != last_page:
            md.append("\n<div class='page-break'></div>\n")
        last_page = page_meta

        # source page label
        md.append(f"<div class='source-page'>Source page: {page_meta}</div>\n")

        text = re.sub(r"\{\d+\}-+", "", c["text"]).strip()

        # fix image path (ABSOLUTE FILE URL)
        if c.get("relative_img_path"):
            img_path = c["relative_img_path"].replace("\\", "/")
            text = re.sub(
                r"!\[.*?\]\(.*?\)",
                f"![](file:///{img_path})",
                text
            )

        # highlight target chunk
        if c["chunk_id"] in target_chunk_id:
            md.append(f"::: highlight\n{text}\n:::\n")
        else:
            md.append(text + "\n")

    return "\n".join(md)

# =========================
# MARKDOWN → HTML
# =========================

def markdown_to_html(md_text):
    return pypandoc.convert_text(
        md_text,
        to="html",
        format="md",
        extra_args=[
            "--mathjax",
            "--wrap=preserve"
        ]
    )

# =========================
# MAIN
# =========================

def create_section_html_from_listchunk(target_chunk_ids):
    citations_dir = os.path.abspath("citations")
    os.makedirs(citations_dir, exist_ok=True)

    file_to_chunks=resolve_file_ids_for_chunks(target_chunk_ids)

    outputs = []

    for file_id, chunk_ids in file_to_chunks.items():
        print(f"\nprocessing file_id:{file_id}")
        print(f"highlighting {len(chunk_ids)} chunks")

        all_chunks = fetch_all_chunks(file_id)

        target = next(c for c in all_chunks if c["chunk_id"]== chunk_ids[0])
        heading = detect_heading(target)

        section_chunks = fetch_chunks_by_header(file_id, heading)

        md = build_section_markdown(
                                    section_chunks,
                                    target_chunk_id=set(chunk_ids),
                                   heading=heading
        )
        html_body = markdown_to_html(md)
        file_stub = f"{file_id[:5]}_{len(chunk_ids)}chunks"
        output_html = os.path.join(
            citations_dir,
            f"{file_stub}_citation.html"
        )

        final_html = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>{heading}</title>
  <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>

  <style>
    body {{
      font-family: Georgia, serif;
      line-height: 1.65;
      margin: 40px;
      max-width: 900px;
    }}

    h1 {{ font-size: 28px; }}
    h2 {{ font-size: 22px; }}
    h3 {{ font-size: 18px; }}

    .source-page {{
      font-size: 12px;
      color: #555;
      margin: 10px 0;
    }}

    .highlight {{
      background: #fff59d;
      padding: 12px;
      border-radius: 4px;
      margin: 12px 0;
    }}

    img {{
      max-width: 100%;
      display: block;
      margin: 16px auto;
    }}

    table {{
      border-collapse: collapse;
      margin: 16px 0;
      width: 100%;
    }}

    th, td {{
      border: 1px solid #ccc;
      padding: 6px 10px;
    }}

    .page-break {{
      margin: 40px 0;
      border-top: 1px dashed #aaa;
    }}
  </style>
</head>
<body>

{html_body}

</body>
</html>
"""

        with open(output_html, "w", encoding="utf-8") as f:
             f.write(final_html)
        
        print("HTML created ->", output_html)
        outputs.append(output_html)
        
    return outputs

def create_section_html_from_chunk(file_id, target_chunk_id):
    citations_dir = os.path.abspath("citations")
    os.makedirs(citations_dir, exist_ok=True)

    # build filename safely
    file_stub = f"{file_id[:5]}{str(target_chunk_id)[-5:]}"
    OUTPUT_HTML = os.path.join(
        citations_dir,
        f"{file_stub}_citation.html"
    )
    
    print("Fetching chunks...")
    all_chunks = fetch_all_chunks(file_id)

    target = next(c for c in all_chunks if c["chunk_id"] == target_chunk_id)
    heading = detect_heading(target)
    print("Heading:", heading)

    section_chunks = fetch_chunks_by_header(file_id, heading)
    print(f"{len(section_chunks)} chunks found")

    md = build_section_markdown(section_chunks, target_chunk_id, heading)
    html_body = markdown_to_html(md)

    final_html = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>{heading}</title>

  <!-- MathJax -->
  <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>

  <style>
    body {{
      font-family: Georgia, serif;
      line-height: 1.65;
      margin: 40px;
      max-width: 900px;
    }}

    h1 {{ font-size: 28px; }}
    h2 {{ font-size: 22px; }}
    h3 {{ font-size: 18px; }}

    .source-page {{
      font-size: 12px;
      color: #555;
      margin: 10px 0;
    }}

    .highlight {{
      background: #fff59d;
      padding: 12px;
      border-radius: 4px;
      margin: 12px 0;
    }}

    img {{
      max-width: 100%;
      display: block;
      margin: 16px auto;
    }}

    table {{
      border-collapse: collapse;
      margin: 16px 0;
      width: 100%;
    }}

    th, td {{
      border: 1px solid #ccc;
      padding: 6px 10px;
    }}

    .page-break {{
      margin: 40px 0;
      border-top: 1px dashed #aaa;
    }}
  </style>
</head>
<body>

{html_body}

</body>
</html>
"""

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(final_html)

    print("✅ HTML created →", OUTPUT_HTML)

    return OUTPUT_HTML


# =======================
# RUN EXAMPLE
# =======================

# if __name__ == "__main__":
#     file_id = "fi_cb52865a-6ff6-4200-85e0-67038ba6ffa3"
#     target_chunk_id = "chk_2ae8a133-db4f-4e8d-8225-bb28ee136004"

#     create_section_html_from_chunk(
#         file_id,
#         target_chunk_id
#     )

if __name__ == "__main__":
    chunk_ids = [
        "chk_e0e7eec5-f6a9-4129-86d4-6cefe1cab7ed",
        "chk_32e6416b-464e-4462-9317-ec4d55c2fa68",
        "chk_6d918c31-2dd5-48bf-9364-47e712286c5e"
    ]

    create_section_html_from_listchunk(chunk_ids)


