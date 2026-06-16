import sys
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

# Print log safely by replacing non-ascii characters
print(logs.encode("ascii", "ignore").decode("ascii"))
