import os
import glob

search_patterns = [
    "*10-1-062_RMT*.csv",
    "*10-1-065_RMH*.csv",
    "*10-1-110_RDP*.csv",
    "*10-3-082_RDP*.csv",
    "*10-1-120_RMT*.csv",
    "*10-1-120_RMH*.csv",
    "*10-1-120_RDP*.csv"
]

found_files = {}
for pattern in search_patterns:
    found = glob.glob(os.path.join(r"D:\ex_work\AirQualityReview_Project\data\csv_b10", "**", pattern), recursive=True)
    if found:
        found_files[pattern] = sorted(found)

for pattern, paths in found_files.items():
    print(f"=== Pattern: {pattern} (Found {len(paths)} files) ===")
    # Print the first file's header and first few lines as a sample
    sample_path = paths[0]
    print(f"Sample file: {os.path.relpath(sample_path, r'D:\ex_work\AirQualityReview_Project')}")
    with open(sample_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = [f.readline().strip() for _ in range(8)]
    for i, line in enumerate(lines):
        print(f"  Line {i+1}: {repr(line)}")
    print("-" * 50)
