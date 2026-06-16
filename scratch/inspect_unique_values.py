import re

file_path = r"D:\ex_work\AirQualityReview_Project\data\csv_b10\101-AHU19\RM065\Raw Data\10-1-065_RMH_2026-05-13_08-48-54-596_1.Csv"
with open(file_path, 'r') as f:
    lines = f.readlines()

values = []
for line in lines[5:]:
    parts = line.strip().split(';')
    if len(parts) >= 3:
        values.append(parts[2])

# Print some unique values
print("Unique scientific values from original file:")
for val in sorted(list(set(values)))[:30]:
    print(val)
