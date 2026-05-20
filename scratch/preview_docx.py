import os
from docx import Document

def extract_docx_text(file_path):
    try:
        doc = Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return "\n".join(full_text)
    except Exception as e:
        return f"Error reading {file_path}: {e}"

root_dir = r"d:\ex_work\AirQualityReview_Project\validation_docs\csv_team_format"

for root, dirs, filenames in os.walk(root_dir):
    for f in filenames:
        if f.endswith(".docx"):
            full_path = os.path.join(root, f)
            print(f"--- FILE: {full_path} ---")
            text = extract_docx_text(full_path)
            print(text[:1000]) # First 1000 chars
            print("\n" + "="*50 + "\n")
