import os
import glob
import re

search_path = r"D:\ex_work\AirQualityReview_Project\data\csv_b10\**\*.Csv"
files = glob.glob(search_path, recursive=True)

found_non_numeric = False
for fpath in files:
    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    for i, line in enumerate(lines[5:]):
        parts = line.strip().split(';')
        if len(parts) >= 3:
            val = parts[2]
            # check if it is not numeric and not scientific notation
            if val and not re.match(r'^-?\d+(\.\d+)?(E[+-]\d+)?$', val):
                print(f"Non-numeric in original {os.path.relpath(fpath, r'D:\ex_work\AirQualityReview_Project')} line {i+6}: {repr(line)}")
                found_non_numeric = True

if not found_non_numeric:
    print("No non-numeric values found in original CSV files.")
