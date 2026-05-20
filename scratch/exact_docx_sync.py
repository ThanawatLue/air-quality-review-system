import os
from docx import Document
import re

def extract_exact_text(docx_path):
    doc = Document(docx_path)
    lines = []
    for p in doc.paragraphs:
        t = p.text.strip()
        if not t:
            # Maybe keep double newlines if needed, but let's just add one
            lines.append("")
            continue
        
        # Try to detect if it's a list item in Word
        # python-docx doesn't easily give the number/bullet character, 
        # but we can check if it's a list style
        prefix = ""
        # Some simple heuristic for lists if text doesn't already have it
        # but the user says "match 100%", so if Word has "1. ", p.text usually has it.
        
        lines.append(p.text)
        
    return "\n".join(lines)

def update_md_with_exact_text(folder, md_file):
    md_path = os.path.join(folder, md_file)
    docx_files = [f for f in os.listdir(folder) if f.endswith(".docx") and "Test Result" in f]
    if not docx_files: return
    
    docx_path = os.path.join(folder, docx_files[0])
    print(f"Extracting 100% exact text from {docx_path} to {md_file}...")
    
    exact_text = extract_exact_text(docx_path)
    
    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()
        
    # Find SECTION 6
    start_match = re.search(r"SECTION \d+: TEST RESULT", md_content, re.IGNORECASE)
    if not start_match: return
    
    start_idx = start_match.end()
    
    # Find SECTION 7
    end_match = re.search(r"\nSECTION \d+:", md_content[start_idx:], re.IGNORECASE)
    if end_match:
        end_idx = start_idx + end_match.start()
    else:
        end_idx = len(md_content)
        
    final_content = md_content[:start_idx] + "\n\n" + exact_text + "\n\n" + md_content[end_idx:]
    
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(final_content)

# Process Appendix 2-5
root = r"d:\ex_work\AirQualityReview_Project\validation_docs\csv_team_format"
apps = [
    ("Appendix 2_Module", "Appendix 2_Module.md"),
    ("Appendix 3_Integration", "Appendix 3_Integration.md"),
    ("Appendix 4_Functional", "Appendix 4_Functional.md"),
    ("Appendix 5_Requirement", "Appendix 5_Requirement.md")
]

for folder, md in apps:
    update_md_with_exact_text(os.path.join(root, folder), md)
