import pandas as pd

file_path = r'D:\ex_work\AirQualityReview_Project\data\csv_main\C\1-P045_05-15-26_01-00.csv'

start_date = None
end_date = None

with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

print("Total lines read:", len(lines))

# Trace start date search
for idx, line in enumerate(lines[:150]):
    if any(sep in line for sep in ['/', '-']):
        parts = line.replace('"', '').split(',')
        for part_idx, part in enumerate(parts):
            part_s = part.strip()
            if any(sep in part_s for sep in ['/', '-']) and len(part_s) >= 8:
                try:
                    dt = pd.to_datetime(part_s, errors='coerce', dayfirst=False)
                    print(f"Line {idx}, Part {part_idx}: {part_s!r} -> {dt}")
                    if pd.notnull(dt) and 2000 < dt.year < 2100:
                        if start_date is None: 
                            start_date = dt.date()
                            print("FOUND START DATE:", start_date)
                        break
                except Exception as ex:
                    print(f"Error on Line {idx}, Part {part_idx} ({part_s!r}):", ex)
        if start_date: break
