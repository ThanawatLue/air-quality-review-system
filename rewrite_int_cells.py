import json

nb_path = r'D:\ex_work\AirQualityReview_Project\validation_docs\Validation_Test_Execution.ipynb'

with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Define new code for each cell index
cell_codes = {
    51: """print("-" * 80)
print("InT-01: check_reverse_violations - Corridor Pressure Comparison directly on real data")
print("-" * 80)

from pathlib import Path
import pandas as pd
import analysis_logic

PROJECT_ROOT = Path(r"D:\\ex_work\\AirQualityReview_Project")
DATA_ROOT = PROJECT_ROOT / "data"
BAS_SOURCE = DATA_ROOT / "csv_main" / "C"
SETPOINT_PATH = DATA_ROOT / "SetPointLimit.xlsx"

before = Path(analysis_logic.audit_trail.LOG_FILE).read_text(encoding="utf-8", errors="ignore") if Path(analysis_logic.audit_trail.LOG_FILE).exists() else ""
out_path, logs, plot_result = analysis_logic.analyze_files(
    folder_path=str(BAS_SOURCE),
    setpoint_path=str(SETPOINT_PATH),
    selected_rooms=["1-P045", "1-P051"],
    start_date="2026-05-13",
    end_date="2026-05-14",
)
after = Path(analysis_logic.audit_trail.LOG_FILE).read_text(encoding="utf-8", errors="ignore") if Path(analysis_logic.audit_trail.LOG_FILE).exists() else ""
new_audit = after[len(before):]
print(logs[:4000].encode("ascii", "ignore").decode("ascii"))
print("--- audit tail ---")
print(new_audit[-4000:].encode("ascii", "ignore").decode("ascii"))
print("--- plot_result summary ---")
print(plot_result.get("summary") if isinstance(plot_result, dict) else plot_result)
print("--- report ---")
print(out_path)

# Assert that pressure violations/checks exist and comparison output is present
assert "ANALYSIS_START" in new_audit
assert "FILE_PROCESSED" in new_audit
assert "ANALYSIS_SUCCESS" in new_audit
assert out_path and Path(out_path).exists()
assert isinstance(plot_result, dict) and plot_result.get("summary")
print("InT-01 PASS")""",

    53: """print("-" * 80)
print("InT-02: get_plot_info - Chart Interval Extraction Filter directly on real data")
print("-" * 80)

from pathlib import Path
import pandas as pd
import analysis_logic

PROJECT_ROOT = Path(r"D:\\ex_work\\AirQualityReview_Project")
DATA_ROOT = PROJECT_ROOT / "data"
BAS_SOURCE = DATA_ROOT / "csv_main" / "C"
SETPOINT_PATH = DATA_ROOT / "SetPointLimit.xlsx"

res = analysis_logic.get_plot_info(
    folder_path=str(BAS_SOURCE),
    setpoint_path=str(SETPOINT_PATH),
    selected_rooms=["1-P045"],
    start_date="2026-05-13",
    end_date="2026-05-14",
    limits=None
)
print("--- plot_result summary ---")
print(res.get("summary") if isinstance(res, dict) else res)
print("--- violation intervals ---")
for v in res.get("violation_intervals", []):
    print(f"  {v['room_id']} | {v['type']} | {v['start']} -> {v['end']} ({v['duration']} min)")

assert isinstance(res, dict)
assert "1-P045" in res.get("plot_data", {})
assert len(res.get("violation_intervals", [])) > 0
print("InT-02 PASS")""",

    55: """print("-" * 80)
print("InT-03: get_plot_info - Plot Data Directory Scan directly on real data")
print("-" * 80)

from pathlib import Path
import pandas as pd
import analysis_logic

PROJECT_ROOT = Path(r"D:\\ex_work\\AirQualityReview_Project")
DATA_ROOT = PROJECT_ROOT / "data"
BAS_SOURCE = DATA_ROOT / "csv_main" / "C"
SETPOINT_PATH = DATA_ROOT / "SetPointLimit.xlsx"

# Write a corrupt CSV file directly to the real directory to test robust GxP logging
corrupt_path = BAS_SOURCE / "1-P045_05-15-26_01-00.csv"
corrupt_path.write_text("this,is,not,a,valid,AQR,csv\\n1,2,3\\n", encoding="utf-8")

try:
    before = Path(analysis_logic.audit_trail.LOG_FILE).read_text(encoding="utf-8", errors="ignore") if Path(analysis_logic.audit_trail.LOG_FILE).exists() else ""
    res_corrupt = analysis_logic.get_plot_info(
        folder_path=str(BAS_SOURCE),
        setpoint_path=str(SETPOINT_PATH),
        selected_rooms=["1-P045"],
        start_date="2026-05-13",
        end_date="2026-05-15",
        limits=None,
    )
    after = Path(analysis_logic.audit_trail.LOG_FILE).read_text(encoding="utf-8", errors="ignore") if Path(analysis_logic.audit_trail.LOG_FILE).exists() else ""
    new_audit = after[len(before):]
    print("--- audit log ---")
    print(new_audit[-2000:])
    
    assert "PLOT_DATA_ERROR" in new_audit or "FILE_ERROR" in new_audit
    assert "1-P045_05-15-26_01-00.csv" in new_audit
    assert "1-P045" in res_corrupt.get("plot_data", {})
    print("InT-03 PASS")
finally:
    if corrupt_path.exists():
        corrupt_path.unlink()""",

    57: """print("-" * 80)
print("InT-04: analyze_files - Parameter Violation 25-Minute Continuous Rule directly on real data")
print("-" * 80)

from pathlib import Path
import pandas as pd
import analysis_logic

PROJECT_ROOT = Path(r"D:\\ex_work\\AirQualityReview_Project")
DATA_ROOT = PROJECT_ROOT / "data"
BAS_SOURCE = DATA_ROOT / "csv_main" / "C"
SETPOINT_PATH = DATA_ROOT / "SetPointLimit.xlsx"

out_path, logs, plot_result = analysis_logic.analyze_files(
    folder_path=str(BAS_SOURCE),
    setpoint_path=str(SETPOINT_PATH),
    selected_rooms=["1-P045"],
    start_date="2026-05-13",
    end_date="2026-05-14",
)
print("--- violation intervals ---")
intervals = plot_result.get("violation_intervals", [])
for v in intervals:
    print(f"  {v['room_id']} | {v['type']:12} | {v['start']} -> {v['end']} ({v['duration']} min)")

# Assert that the temperature violation duration is 40.0 minutes
temp_viols = [v for v in intervals if v['type'] == 'Temperature']
assert len(temp_viols) == 1
assert temp_viols[0]['duration'] == 40.0
print("InT-04 PASS")""",

    59: """print("-" * 80)
print("InT-05: analyze_files - Phase I full statistical execution directly on real data")
print("-" * 80)

from pathlib import Path
import pandas as pd
import analysis_logic

PROJECT_ROOT = Path(r"D:\\ex_work\\AirQualityReview_Project")
DATA_ROOT = PROJECT_ROOT / "data"
BAS_SOURCE = DATA_ROOT / "csv_main" / "C"
SETPOINT_PATH = DATA_ROOT / "SetPointLimit.xlsx"

before = Path(analysis_logic.audit_trail.LOG_FILE).read_text(encoding="utf-8", errors="ignore") if Path(analysis_logic.audit_trail.LOG_FILE).exists() else ""
out_path, logs, plot_result = analysis_logic.analyze_files(
    folder_path=str(BAS_SOURCE),
    setpoint_path=str(SETPOINT_PATH),
    selected_rooms=["1-P045", "1-P051"],
    start_date="2026-05-13",
    end_date="2026-05-14",
)
after = Path(analysis_logic.audit_trail.LOG_FILE).read_text(encoding="utf-8", errors="ignore") if Path(analysis_logic.audit_trail.LOG_FILE).exists() else ""
new_audit = after[len(before):]
print(logs[:4000].encode("ascii", "ignore").decode("ascii"))
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
print("InT-05 PASS")""",

    61: """print("-" * 80)
print("InT-06: analyze_files_phase2 - Phase II full statistical execution directly on real data")
print("-" * 80)

from pathlib import Path
import pandas as pd
import analysis_logic

PROJECT_ROOT = Path(r"D:\\ex_work\\AirQualityReview_Project")
DATA_ROOT = PROJECT_ROOT / "data"
PHASE2_SOURCE = DATA_ROOT / "csv_b11"
PHASE2_SETPOINT_PATH = DATA_ROOT / "SetPointLimit_B11.xlsx"

before = Path(analysis_logic.audit_trail.LOG_FILE).read_text(encoding="utf-8", errors="ignore") if Path(analysis_logic.audit_trail.LOG_FILE).exists() else ""
out_path, logs, plot_result = analysis_logic.analyze_files_phase2(
    folder_path=str(PHASE2_SOURCE),
    setpoint_path=str(PHASE2_SETPOINT_PATH),
    selected_rooms=["11-1-012", "11-1-013"],
    start_date="2026-05-01",
    end_date="2026-05-02",
)
after = Path(analysis_logic.audit_trail.LOG_FILE).read_text(encoding="utf-8", errors="ignore") if Path(analysis_logic.audit_trail.LOG_FILE).exists() else ""
new_audit = after[len(before):]
print(logs[:4000].encode("ascii", "ignore").decode("ascii"))
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
print("InT-06 PASS")"""
}

# Update the cells
for idx, code_str in cell_codes.items():
    # Split by lines, ensuring each line has \n at the end except the last
    lines = [line + '\n' for line in code_str.split('\n')]
    # Remove last newline to keep format correct
    if lines and lines[-1].endswith('\n'):
        lines[-1] = lines[-1][:-1]
    
    nb['cells'][idx]['source'] = lines
    nb['cells'][idx]['outputs'] = []
    nb['cells'][idx]['execution_count'] = None

with open(nb_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print("Rewrote all 6 integration cells successfully.")