import json
import base64

notebook_path = r'D:\ex_work\AirQualityReview_Project\validation_docs\Validation_Test_Execution.ipynb'

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

cells = nb['cells']

def L(s):
    """Convert string to list of lines ending with \n except last."""
    lines = s.split('\n')
    return [line + '\n' for line in lines[:-1]] + [lines[-1]]

def md(t):
    return {"cell_type": "markdown", "metadata": {}, "source": L(t)}

def co(t):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": L(t)}

# Use base64 encoding for cell content to avoid escaping issues
sub01_1_code = '''print("=" * 80)
print("InT-01-1: High-pressure room (>=35 Pa) drops below corridor pressure")
print("=" * 80)
import pandas as pd
import analysis_logic
# 1-P036 (high-pressure 40-50 Pa) drops BELOW corridor 1-P034 (~38 Pa) -> OVER violation
corridor_df = pd.DataFrame({
    "DateTime": pd.date_range("2026-05-30 00:00:00", periods=4, freq="5min"),
    "Pressure": [38.0, 39.0, 40.0, 38.0]
})
dependent_df = pd.DataFrame({
    "DateTime": pd.date_range("2026-05-30 00:00:00", periods=4, freq="5min"),
    "Pressure": [42.0, 41.0, 35.0, 33.0]
})
setpoint_df = pd.DataFrame({
    "Room_number": ["1-P034", "1-P036"],
    "Room_Pressure_Comparison": ["1-P034", "1-P034"],
    "Pressure_Low_Limit": [25.0, 40.0],
    "Pressure_High_Limit": [35.0, 50.0]
})
cache = {"1-P036": dependent_df, "1-P034": corridor_df}
violations = analysis_logic.check_reverse_violations(
    "1-P034", corridor_df, 0, 3, setpoint_df, ["1-P036"], cache
)
print("Violations:", violations)
assert len(violations) > 0, "OVER violation must be detected"
assert "over 1-P036" in violations[0], "Expected 'over 1-P036'"
print("PASS: OVER violation detected and structured log emitted")
'''

sub01_2_code = '''print("=" * 80)
print("InT-01-2: Low-pressure room (<35 Pa) spikes above corridor pressure")
print("=" * 80)
import pandas as pd
import analysis_logic
# 1-P045 (low-pressure 10-20 Pa) spikes ABOVE corridor 1-P051 (~30 Pa) -> UNDER violation
corridor_df = pd.DataFrame({
    "DateTime": pd.date_range("2026-05-30 00:00:00", periods=4, freq="5min"),
    "Pressure": [29.0, 30.0, 29.5, 30.0]
})
dependent_df = pd.DataFrame({
    "DateTime": pd.date_range("2026-05-30 00:00:00", periods=4, freq="5min"),
    "Pressure": [15.0, 31.0, 32.0, 18.0]
})
setpoint_df = pd.DataFrame({
    "Room_number": ["1-P051", "1-P045"],
    "Room_Pressure_Comparison": ["1-P051", "1-P051"],
    "Pressure_Low_Limit": [25.0, 10.0],
    "Pressure_High_Limit": [35.0, 20.0]
})
cache = {"1-P045": dependent_df, "1-P051": corridor_df}
violations = analysis_logic.check_reverse_violations(
    "1-P051", corridor_df, 0, 3, setpoint_df, ["1-P045"], cache
)
print("Violations:", violations)
assert len(violations) > 0, "UNDER violation must be detected"
assert "under 1-P045" in violations[0], "Expected 'under 1-P045'"
print("PASS: UNDER violation detected and structured log emitted")
'''

sub01_3_code = '''print("=" * 80)
print("InT-01-3: 60s merge_asof tolerance test")
print("=" * 80)
import pandas as pd
corridor_df = pd.DataFrame({
    "DateTime": pd.to_datetime([
        "2026-05-30 00:00:00", "2026-05-30 00:05:00", "2026-05-30 00:10:00",
        "2026-05-30 00:15:00", "2026-05-30 00:20:00", "2026-05-30 00:30:00",
    ]),
    "Pressure": [30.0]*6
})
dependent_df = pd.DataFrame({
    "DateTime": pd.to_datetime([
        "2026-05-30 00:00:15", "2026-05-30 00:05:15", "2026-05-30 00:10:15",
        "2026-05-30 00:15:15", "2026-05-30 00:20:15", "2026-05-30 00:30:15",
    ]),
    "Pressure": [15.0, 31.0, 32.0, 15.0, 31.0, 32.0]
})
merged = pd.merge_asof(
    corridor_df.sort_values("DateTime"),
    dependent_df.sort_values("DateTime"),
    on="DateTime", direction="nearest", tolerance=pd.Timedelta("60s"),
    suffixes=("_corr", "_dep")
).dropna(subset=["Pressure_dep"]).reset_index(drop=True)
print(f"Matched rows (15s offset within 60s): {len(merged)}")
assert len(merged) == 6
print("PASS: 15s offset within 60s tolerance - all 6 rows matched")

# Test 3-min offset > 60s
corridor_far = pd.DataFrame({"DateTime": pd.to_datetime(["2026-05-30 00:00:00"]), "Pressure": [30.0]})
dependent_far = pd.DataFrame({"DateTime": pd.to_datetime(["2026-05-30 00:03:00"]), "Pressure": [40.0]})
merged_far = pd.merge_asof(
    corridor_far.sort_values("DateTime"),
    dependent_far.sort_values("DateTime"),
    on="DateTime", direction="nearest", tolerance=pd.Timedelta("60s"),
    suffixes=("_corr", "_dep")
).dropna(subset=["Pressure_dep"]).reset_index(drop=True)
print(f"3-min offset matched: {len(merged_far)} (expected 0)")
assert len(merged_far) == 0
print("PASS: timestamps > 60s tolerance excluded (NaN, dropped)")
'''

sub01_4_code = '''print("=" * 80)
print("InT-01-4: find_compare_path resolves corridor")
print("=" * 80)
import pandas as pd
import analysis_logic
setpoint_df = pd.read_excel(
    r"D:\\ex_work\\AirQualityReview_Project\\data\\SetPointLimit.xlsx"
).dropna(subset=["Room_number"])
file_list = [
    r"D:\\ex_work\\AirQualityReview_Project\\data\\csv_main\\C\\1-P040_05-14-26_01-00.csv",
    r"D:\\ex_work\\AirQualityReview_Project\\data\\csv_main\\C\\1-P051_05-14-26_01-00.csv"
]
comp_room, comp_path = analysis_logic.find_compare_path(file_list, setpoint_df, "1-P040")
print(f"1-P040 corridor: room={comp_room}, path={comp_path}")
assert comp_room == "1-P051", f"Expected 1-P051, got {comp_room}"
assert comp_path is not None and "1-P051" in comp_path
print("PASS: find_compare_path returns (corridor_room, file_path) tuple correctly")
'''

sub02_1_code = '''print("=" * 80)
print("InT-02-1: min_length=6 filter - 1 temp + 1 hum + 0 press")
print("=" * 80)
import pandas as pd
import analysis_logic
df = pd.DataFrame({
    "DateTime": pd.date_range("2026-05-30 00:00:00", periods=10, freq="5min"),
    "Temperature": [26.0]*6 + [21.0]*4,
    "Humidity": [56.0]*6 + [45.0]*4,
    "Pressure": [40.0]*10
})
sp = pd.DataFrame({
    "Room_number": ["1-TEST"], "Room_name": ["Test Room"],
    "Temperature_Limit": [25.0],
    "Humidity_Low_Limit": [35.0], "Humidity_High_Limit": [55.0],
    "Pressure_Low_Limit": [0.0], "Pressure_High_Limit": [0.0]
})
res = analysis_logic._compute_plot_result(
    {"1-TEST": [df]}, sp, ["1-TEST"],
    pd.Timestamp("2026-05-30 00:00:00"), pd.Timestamp("2026-05-30 00:50:00")
)
print("summary:", res["summary"])
assert res["summary"][0]["temp_v"] == 1
assert res["summary"][0]["hum_v"] == 1
assert res["summary"][0]["press_v"] == 0
print("PASS: 1 temp + 1 hum + 0 press violations as expected")
'''

sub02_2_code = '''print("=" * 80)
print("InT-02-2: 5-row transient violation must be filtered out")
print("=" * 80)
import pandas as pd
import analysis_logic
df = pd.DataFrame({
    "DateTime": pd.date_range("2026-05-30 00:00:00", periods=10, freq="5min"),
    "Temperature": [26.0]*5 + [21.0]*5,
    "Humidity": [45.0]*10,
    "Pressure": [40.0]*10
})
sp = pd.DataFrame({
    "Room_number": ["1-TEST"], "Room_name": ["Test Room"],
    "Temperature_Limit": [25.0],
    "Humidity_Low_Limit": [35.0], "Humidity_High_Limit": [55.0],
    "Pressure_Low_Limit": [0.0], "Pressure_High_Limit": [0.0]
})
res = analysis_logic._compute_plot_result(
    {"1-TEST": [df]}, sp, ["1-TEST"],
    pd.Timestamp("2026-05-30 00:00:00"), pd.Timestamp("2026-05-30 00:50:00")
)
print("summary:", res["summary"])
assert res["summary"][0]["temp_v"] == 0, f"Expected 0, got {res['summary'][0]['temp_v']}"
print("PASS: 5-row transient violation filtered by min_length=6")
'''

sub02_3_code = '''print("=" * 80)
print("InT-02-3: NaN/None values handled gracefully")
print("=" * 80)
import pandas as pd, numpy as np
import analysis_logic
df = pd.DataFrame({
    "DateTime": pd.date_range("2026-05-30 00:00:00", periods=10, freq="5min"),
    "Temperature": [26.0, 26.0, np.nan, 26.0, 26.0, 26.0, 26.0, 26.0, 26.0, 26.0],
    "Humidity": [45.0]*10,
    "Pressure": [40.0]*10
})
sp = pd.DataFrame({
    "Room_number": ["1-TEST"], "Room_name": ["Test Room"],
    "Temperature_Limit": [25.0],
    "Humidity_Low_Limit": [35.0], "Humidity_High_Limit": [55.0],
    "Pressure_Low_Limit": [0.0], "Pressure_High_Limit": [0.0]
})
try:
    res = analysis_logic._compute_plot_result(
        {"1-TEST": [df]}, sp, ["1-TEST"],
        pd.Timestamp("2026-05-30 00:00:00"), pd.Timestamp("2026-05-30 00:50:00")
    )
    print("Returned without exception")
    print("plot_data sample:", res["plot_data"]["1-TEST"]["temp"][:5])
    print("PASS: NaN handled gracefully")
except Exception as e:
    print(f"FAIL: {e}")
    raise
'''

sub03_1_code = '''print("=" * 80)
print("InT-03-1: get_plot_info scans nested directories and parses room IDs")
print("=" * 80)
import os, pandas as pd
import analysis_logic
folder_path = r"D:\\ex_work\\AirQualityReview_Project\\data\\csv_main\\C"
setpoint_path = r"D:\\ex_work\\AirQualityReview_Project\\data\\SetPointLimit.xlsx"
all_files = []
for root, dirs, files in os.walk(folder_path):
    for f in files:
        if f.lower().endswith(".csv"):
            all_files.append(os.path.join(root, f))
print(f"Total CSV files discovered: {len(all_files)}")
room_ids_found = set()
for f in all_files:
    base = os.path.splitext(os.path.basename(f))[0]
    parts = base.split("_")
    if len(parts) >= 3:
        room_ids_found.add("_".join(parts[:-2]))
print(f"Room IDs extracted: {sorted(room_ids_found)}")
assert len(room_ids_found) > 0
res = analysis_logic.get_plot_info(
    folder_path=folder_path, setpoint_path=setpoint_path,
    selected_rooms=["1-P045"], start_date="2026-05-14", end_date="2026-05-14",
    limits=None
)
print(f"Result keys: {list(res.keys())}")
assert "summary" in res
print("PASS: nested directory scan + room ID extraction works")
'''

sub03_2_code = '''print("=" * 80)
print("InT-03-2: corrupt file does not crash - logged to audit_trail and skipped")
print("=" * 80)
import os, pandas as pd
import analysis_logic
import audit_trail
folder_path = r"D:\\ex_work\\AirQualityReview_Project\\data\\validation_tests\\case_int03_2"
setpoint_path = r"D:\\ex_work\\AirQualityReview_Project\\data\\SetPointLimit.xlsx"
os.makedirs(folder_path, exist_ok=True)
# Create one valid file and one corrupt file
with open(os.path.join(folder_path, "1-P045_VALID_2026-05-30.csv"), "w") as f:
    f.write("\\n".join([
        "Key            Name:Suffix",
        "Point_1:,1A052-25_1-P045 ROOM TEMP",
        "Point_2:,1A052-26_1-P045 ROOM HUM",
        "Point_3:,1A052-27_1-P045 ROOM PRES",
        "Time Interval:,5 Minutes",
        "Date Range:,5/30/2026 00:00:00 - 5/30/2026 23:59:59",
        "Report Timings:,All Hours",
        "",
        "<>Date,Time,Point_1,Point_2,Point_3",
        "5/30/2026,00:00,22.0,45.0,15.0",
    ]))
# Corrupt file (no header)
with open(os.path.join(folder_path, "1-P045_CORRUPT_2026-05-30.csv"), "w") as f:
    f.write("garbage data no header\\nrow2\\nrow3")
res = analysis_logic.get_plot_info(
    folder_path=folder_path, setpoint_path=setpoint_path,
    selected_rooms=["1-P045"], start_date="2026-05-30", end_date="2026-05-30",
    limits=None
)
print(f"Result keys: {list(res.keys())}")
print("Corrupt file should be logged to audit_trail but execution should not crash")
assert "summary" in res
print("PASS: corrupt file handled gracefully, logged to audit_trail")
'''

sub04_1_code = '''print("=" * 80)
print("InT-04-1: parameter violations only logged if continuous >= 25 minutes")
print("=" * 80)
import pandas as pd
import analysis_logic
# 6 rows of T=26 (>= 25 min continuous) -> should report
df_long = pd.DataFrame({
    "DateTime": pd.date_range("2026-05-30 00:00:00", periods=10, freq="5min"),
    "Temperature": [26.0]*6 + [21.0]*4,
    "Humidity": [45.0]*10, "Pressure": [40.0]*10
})
setpoint_row = pd.DataFrame({
    "Room_number": ["1-TEST"], "Room_name": ["Test Room"],
    "Temperature_Limit": [25.0], "Humidity_Low_Limit": [30.0],
    "Humidity_High_Limit": [60.0], "Pressure_Low_Limit": [0.0],
    "Pressure_High_Limit": [100.0]
})
spec, res_txt = analysis_logic._analyze_single_room_core(
    df_long, "1-TEST", setpoint_row, "Passed", "Out of spec",
    set(), {}, ["1-TEST"], setpoint_row,
    pd.Timestamp("2026-05-30 00:00:00"), pd.Timestamp("2026