import os
from docx import Document

root_dir = r"d:\ex_work\AirQualityReview_Project\validation_docs\csv_team_format"

print(f"Scanning: {root_dir}")
for root, dirs, filenames in os.walk(root_dir):
    for f in filenames:
        if f.endswith(".md") or f.endswith(".docx"):
            full_path = os.path.join(root, f)
            print(full_path)
