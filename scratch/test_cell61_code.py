import sys
from pathlib import Path
import pandas as pd
sys.path.append(r'D:\ex_work\AirQualityReview_Project')
import analysis_logic

PROJECT_ROOT = Path(r"D:\ex_work\AirQualityReview_Project")
DATA_ROOT = PROJECT_ROOT / "data"
PHASE2_SOURCE = DATA_ROOT / "csv_b10"
PHASE2_SETPOINT_PATH = DATA_ROOT / "SetPointLimit_B10.xlsx"

# Define a mock display function since we are not in IPython
def display(df):
    print(df.to_string())

setpoint_df_p2 = pd.read_excel(str(PHASE2_SETPOINT_PATH))
room_id, df_sample, sensors = analysis_logic.prepare_df_phase2(str(PHASE2_SOURCE), "10-1-096", setpoint_df_p2)
print("--- Sample DataFrame for Room 10-1-096 ---")
display(df_sample.head())

before = Path(analysis_logic.audit_trail.LOG_FILE).read_text(encoding="utf-8", errors="ignore") if Path(analysis_logic.audit_trail.LOG_FILE).exists() else ""
out_path, logs, plot_result = analysis_logic.analyze_files_phase2(
    folder_path=str(PHASE2_SOURCE),
    setpoint_path=str(PHASE2_SETPOINT_PATH),
    selected_rooms=["10-1-096", "10-1-097", "10-1-098"],
    start_date="2026-05-12",
    end_date="2026-05-12",
)
after = Path(analysis_logic.audit_trail.LOG_FILE).read_text(encoding="utf-8", errors="ignore") if Path(analysis_logic.audit_trail.LOG_FILE).exists() else ""
new_audit = after[len(before):]
print(logs.encode("ascii", "ignore").decode("ascii"))
print("--- audit tail ---")
print(new_audit[-4000:].encode("ascii", "ignore").decode("ascii"))
print("--- plot_result summary ---")
print(plot_result.get("summary") if isinstance(plot_result, dict) else plot_result)
print("--- report ---")
print(out_path)

assert "ANALYSIS_START" in new_audit
assert "FILE_PROCESSED" in new_audit
assert "ANALYSIS_SUCCESS" in new_audit
assert out_path and Path(out_path).exists() and Path(out_path).stat().st_size > 0
assert isinstance(plot_result, dict) and plot_result.get("summary")
print("InT-06 PASS")
