import sys
import os
import pandas as pd

# Add the workspace directory to the path so we can import analysis_logic
sys.path.append("d:/ex_work/AirQualityReview_Project")

import analysis_logic
import audit_trail

print("Verifying Phase 2 Analysis logic...")

folder_path = r"D:\ex_work\AirQualityReview_Project\data\2026-05"
setpoint_path = r"D:\ex_work\AirQualityReview_Project\data\SetPointLimit_B11.xlsx"

# Scan rooms recursively
print("Scanning rooms in folder tree...")
room_scan = analysis_logic.scan_phase2_rooms(folder_path)
print(f"Total unique rooms found: {len(room_scan)}")

# Run test range from 2026-05-01 to 2026-05-18
start_date = "2026-05-01"
end_date = "2026-05-18"
selected_rooms = ["11-1-012", "11-1-013"]

print(f"\nRunning analysis for selected rooms: {selected_rooms} from {start_date} to {end_date}...")
output_path, logs, plot_result = analysis_logic.analyze_files_phase2(
    folder_path=folder_path,
    setpoint_path=setpoint_path,
    selected_rooms=selected_rooms,
    start_date=start_date,
    end_date=end_date
)

if output_path:
    print(f"\nSUCCESS: Report generated at: {output_path}")
    print(f"Stats: {plot_result.get('stats') if plot_result else 'No stats'}")
    
    # Read the output Excel file to verify dates and room records
    print("\nReading generated Excel file to verify content...")
    xl = pd.ExcelFile(output_path)
    df_report = xl.parse("Report")
    
    print("\nExcel Columns:")
    print(df_report.columns)
    print("\nFirst 40 rows:")
    # We display up to 40 rows to see multiple dates and room records
    for idx, row in df_report.iloc[:40].iterrows():
        row_str = str(list(row))
        # Safely print by encoding to utf-8 and back to prevent Windows console errors
        print(f"Row {idx}: {row_str.encode('ascii', errors='replace').decode('ascii')}")
else:
    print("\nFAILURE: No report generated.")
    print("Logs:")
    print(logs)
