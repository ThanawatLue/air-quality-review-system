import os
from docx import Document
import re
from docx.enum.style import WD_STYLE_TYPE

def extract_exact_text_with_lists(docx_path):
    doc = Document(docx_path)
    lines = []
    
    # We need to keep track of numbering for lists
    # This is a bit complex in python-docx, so we'll use a simple heuristic
    # If a paragraph has a list-like style or if it's clearly a step
    
    for p in doc.paragraphs:
        text = p.text.strip()
        if not text:
            lines.append("")
            continue
            
        # Check if it's a "Test Case" header
        if re.search(r"^[A-Z]Q-TC-\d+", text):
            lines.append(f"\n### {text}")
            continue
            
        # Check for Objective, Procedure, Acceptance Criteria, Results
        if text.lower().startswith("objective:") or \
           text.lower().startswith("procedure:") or \
           text.lower().startswith("acceptance criteria:") or \
           text.lower().startswith("results:"):
            lines.append(f"\n**{text}**")
            continue
            
        # If it's a list item, Word usually doesn't put the number in .text
        # We'll try to detect it. 
        # For simplicity, if it's under Procedure or Acceptance Criteria and doesn't have a number, 
        # we might want to add one. But "100% exact" might mean "don't guess".
        
        # However, the user complained about missing bullets.
        # Let's check the style
        if "List" in p.style.name:
            lines.append(f"- {text}")
        else:
            lines.append(text)
            
    return "\n".join(lines)

def update_md(folder, md_file):
    md_path = os.path.join(folder, md_file)
    docx_files = [f for f in os.listdir(folder) if f.endswith(".docx") and "Test Result" in f]
    if not docx_files: return
    
    docx_path = os.path.join(folder, docx_files[0])
    text = extract_exact_text_with_lists(docx_path)
    
    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()
        
    start_marker = "SECTION 6: TEST RESULT"
    end_marker = "SECTION 7: CRITERIA" # Note: App 1 has SECTION 8, others have 7
    
    # Generic find next section
    start_match = re.search(r"SECTION \d+: TEST RESULT", md_content, re.IGNORECASE)
    if not start_match: return
    start_idx = start_match.end()
    
    end_match = re.search(r"\nSECTION \d+:", md_content[start_idx:], re.IGNORECASE)
    if end_match:
        end_idx = start_idx + end_match.start()
    else:
        end_idx = len(md_content)
        
    final = md_content[:start_idx] + "\n\n" + text + "\n\n" + md_content[end_idx:]
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(final)

root = r"d:\ex_work\AirQualityReview_Project\validation_docs\csv_team_format"
apps = [
    ("Appendix 2_Module", "Appendix 2_Module.md"),
    ("Appendix 3_Integration", "Appendix 3_Integration.md"),
    ("Appendix 4_Functional", "Appendix 4_Functional.md"),
    ("Appendix 5_Requirement", "Appendix 5_Requirement.md")
]

for folder, md in apps:
    update_md(os.path.join(root, folder), md)
