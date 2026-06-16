import os
import random

target_dir = r"D:\ex_work\AirQualityReview_Project\data\csv_main\C"
target_file = os.path.join(target_dir, "1-P045_05-15-26_01-00.csv")

random.seed(12345)

lines = [
    "Key            Name:Suffix                                Trend Definitions Used,,,,\n",
    "Point_1:,1A052-25_1-P045 ROOM TEMP,,5 minutes,\n",
    "Point_2:,1A052-26_1-P045 ROOM HUM,,5 minutes,\n",
    "Point_3:,1A052-27_1-P045 ROOM PRES,,5 minutes,\n",
    "Time Interval:,5 Minutes,,,\n",
    "Date Range:,5/14/2026 00:00:00 - 5/14/2026 23:59:59,,,\n",
    "Report Timings:,All Hours,,,\n",
    ",,,,\n",
    "<>Date,Time,Point_1,Point_2,Point_3\n"
]

# Generate 288 records (5-minute interval for 24 hours)
for hour in range(24):
    for minute in range(0, 60, 5):
        time_str = f"{hour:02d}:{minute:02d}:00"
        
        # Temp: stable around 21.5°C (range 21.2 to 21.8)
        temp = round(21.5 + random.uniform(-0.3, 0.3), 1)
        
        # Hum: stable around 37.5% (range 36.8 to 38.2)
        hum = round(37.5 + random.uniform(-0.7, 0.7), 1)
        
        # Pres: stable around 15.0 Pa (range 14.2 to 15.8)
        pres = round(15.0 + random.uniform(-0.8, 0.8), 1)
        
        lines.append(f"5/14/2026,{time_str},{temp},{hum},{pres}\n")

lines.append(" ******************************** End of Report *********************************,,,,\n")

with open(target_file, "w", encoding="utf-8") as f:
    f.writelines(lines)

print(f"Successfully generated {target_file} with 288 rows of realistic GxP data.")
