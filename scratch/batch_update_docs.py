import os
from docx import Document
import re
import subprocess

def extract_clean_docx_content(docx_path):
    doc = Document(docx_path)
    lines = []
    for p in doc.paragraphs:
        text = p.text.strip()
        if not text: continue
        
        # Detect headers/sections
        if re.search(r"^[A-Z]Q-TC-\d+", text):
            lines.append(f"\n### {text}")
        elif text.startswith("Objective:") or text.startswith("Procedure:") or text.startswith("Acceptance Criteria:") or text.startswith("Results:"):
            lines.append(f"\n**{text}**")
        elif text.startswith("•") or text.startswith("-"):
            lines.append(f"   {text}")
        elif re.match(r"^\d+\.", text): # Numbered steps
            lines.append(f"   {text}")
        else:
            # Bullet everything else in procedure/objective
            lines.append(f"   - {text}")
    return "\n".join(lines)

def update_appendix(folder_path, md_filename):
    md_path = os.path.join(folder_path, md_filename)
    if not os.path.exists(md_path): return
    
    # Find all docx files and extract their content
    docx_files = [f for f in os.listdir(folder_path) if f.endswith(".docx") and "Test Result" in f]
    if not docx_files:
        # Fallback to any docx if no "Test Result" one
        docx_files = [f for f in os.listdir(folder_path) if f.endswith(".docx")]
        
    if not docx_files: return
    
    # Sort them (Enclosure 1, 2, then Result)
    docx_files.sort()
    
    # Extract from the "Test Result" docx specifically if it exists, as it usually has the procedure+results
    result_docx = [f for f in docx_files if "Test Result" in f]
    source_docx = result_docx[0] if result_docx else docx_files[-1]
    
    print(f"Updating {md_filename} using {source_docx}...")
    new_content = extract_clean_docx_content(os.path.join(folder_path, source_docx))
    
    with open(md_path, "r", encoding="utf-8") as f:
        old_md = f.read()
        
    # Find Test Result section
    # Search for SECTION 6 or similar
    start_match = re.search(r"SECTION \d+: TEST RESULT", old_md, re.IGNORECASE)
    if not start_match:
        start_match = re.search(r"## TEST RESULT", old_md, re.IGNORECASE)
        
    if not start_match:
        print(f"  Could not find Test Result section in {md_filename}")
        return
        
    start_idx = start_match.end()
    
    # Find the next section
    end_match = re.search(r"\nSECTION \d+:", old_md[start_idx:], re.IGNORECASE)
    if not end_match:
        end_match = re.search(r"\n## ", old_md[start_idx:])
        
    if end_match:
        end_idx = start_idx + end_match.start()
    else:
        end_idx = len(old_md)
        
    final_md = old_md[:start_idx] + "\n" + new_content + "\n\n" + old_md[end_idx:]
    
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(final_md)

root_dir = r"d:\ex_work\AirQualityReview_Project\validation_docs\csv_team_format"
subdirs = [
    ("Appendix 1_FRA", "Appendix 1_FRA.md"),
    ("Appendix 2_Module", "Appendix 2_Module.md"),
    ("Appendix 3_Integration", "Appendix 3_Integration.md"),
    ("Appendix 4_Functional", "Appendix 4_Functional.md"),
    ("Appendix 5_Requirement", "Appendix 5_Requirement.md")
]

# Restore all first to ensure clean state
# On Windows, we might need a simpler glob or just list the files
for folder, md in subdirs:
    subprocess.run(["git", "restore", f"validation_docs/csv_team_format/{folder}/{md}"])

for folder, md in subdirs:
    update_appendix(os.path.join(root_dir, folder), md)

print("Batch update complete.")
