file_path = r"D:\ex_work\AirQualityReview_Project\data\csv_b10\103-AHU17\RM082\Raw Data\10-3-082_RDP_2026-05-13_08-31-35-542_1.Csv"
with open(file_path, 'r') as f:
    lines = f.readlines()

values = []
for line in lines[5:]:
    parts = line.strip().split(';')
    if len(parts) >= 3:
        values.append(parts[2])

print("Unique values in RM082 RDP (pressure):")
for val in sorted(list(set(values)))[:40]:
    print(val)
