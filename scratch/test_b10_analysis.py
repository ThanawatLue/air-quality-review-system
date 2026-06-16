import sys
from pathlib import Path
import pandas as pd
sys.path.append(r'D:\ex_work\AirQualityReview_Project')
import analysis_logic

folder_path = r'D:\ex_work\AirQualityReview_Project\data\csv_b10'
setpoint_path = r'D:\ex_work\AirQualityReview_Project\data\SetPointLimit_B10.xlsx'
selected_rooms = ["10-1-096", "10-1-097", "10-1-098"]

out_path, logs, plot_result = analysis_logic.analyze_files_phase2(
    folder_path=folder_path,
    setpoint_path=setpoint_path,
    selected_rooms=selected_rooms,
    start_date="2026-05-12",
    end_date="2026-05-13 23:55:00"
)

print("Output Path:", out_path)
print("Plot Result Summary:", plot_result.get("summary") if isinstance(plot_result, dict) else plot_result)
print("Violations printed in logs:")
for line in logs.splitlines():
    if 'Violations' in line or 'Interval' in line or 'Processing' in line or 'Completed' in line:
        print('  ', line)
