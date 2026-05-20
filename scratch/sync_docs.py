import os
from docx import Document

def docx_to_md(docx_path):
    doc = Document(docx_path)
    md_output = []
    
    # We use a set to track which tables and paragraphs we've processed 
    # because iterate through body elements is safer for order.
    
    import docx.table
    import docx.text.paragraph
    
    for block in iter_block_items(doc):
        if isinstance(block, docx.text.paragraph.Paragraph):
            text = block.text.strip()
            if text:
                # Basic header detection (if all caps or starts with SECTION)
                if text.isupper() or text.startswith("SECTION"):
                    md_output.append(f"## {text}\n")
                else:
                    md_output.append(text + "\n")
        elif isinstance(block, docx.table.Table):
            md_table = []
            for i, row in enumerate(block.rows):
                # Clean cell text
                cells = [cell.text.strip().replace('\n', '<br>').replace('|', '\\|') for cell in row.cells]
                md_table.append("| " + " | ".join(cells) + " |")
                if i == 0:
                    md_table.append("| " + " | ".join(["---"] * len(cells)) + " |")
            md_output.append("\n" + "\n".join(md_table) + "\n")
            
    return "\n".join(md_output)

def iter_block_items(parent):
    """
    Yield are either Paragraph or Table objects from parent.
    """
    from docx.document import Document as _Document
    from docx.oxml.table import CT_Tbl
    from docx.oxml.text.paragraph import CT_P
    from docx.table import Table
    from docx.text.paragraph import Paragraph

    if isinstance(parent, _Document):
        parent_elm = parent.element.body
    else:
        raise TypeError("Parent must be Document")

    for child in parent_elm.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, parent)
        elif isinstance(child, CT_Tbl):
            yield Table(child, parent)

root_dir = r"d:\ex_work\AirQualityReview_Project\validation_docs\csv_team_format"

for root, dirs, filenames in os.walk(root_dir):
    md_files = [f for f in filenames if f.endswith(".md")]
    docx_files = [f for f in filenames if f.endswith(".docx")]
    
    if not md_files or not docx_files:
        continue
        
    # Pick the most relevant MD file (usually the one matching the folder name or Appendix X)
    target_md = md_files[0] 
    # If there are multiple, try to find one that doesn't have "TeamFormat" in name if possible
    for m in md_files:
        if "TeamFormat" not in m:
            target_md = m
            break
            
    md_path = os.path.join(root, target_md)
    print(f"Updating {md_path}...")
    
    combined_content = []
    # Sort docx files to have some consistent order (Enclosure 1, then 2, etc.)
    docx_files.sort()
    
    for df in docx_files:
        df_path = os.path.join(root, df)
        print(f"  Extracting {df_path}...")
        combined_content.append(f"# From {df}\n")
        combined_content.append(docx_to_md(df_path))
        combined_content.append("\n---\n")
        
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(combined_content))
    print(f"Done updating {target_md}")
