import os
import glob
import re

search_path = r"D:\ex_work\AirQualityReview_Project\data\CSV B.10 AQR\**\*.csv"
files = glob.glob(search_path, recursive=True)

for fpath in sorted(files):
    if "_fallback" in fpath:
        continue
    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = [f.readline().strip() for _ in range(8)]
    
    # Check delimiter in line 5 (which should be header)
    line5 = lines[4] if len(lines) > 4 else ""
    delimiter = ";" if ";" in line5 else ","
    
    # Check first data row (line 6)
    line6 = lines[5] if len(lines) > 5 else ""
    
    print(f"File: {os.path.relpath(fpath, r'D:\ex_work\AirQualityReview_Project')}")
    print(f"  Delim: {delimiter}")
    print(f"  Line 1: {repr(lines[0])}")
    print(f"  Line 5: {repr(lines[4])}")
    print(f"  Line 6: {repr(lines[5])}")
    print("-" * 50)
