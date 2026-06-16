import pandas as pd
import sys, os
sys.path.append(r'D:\ex_work\AirQualityReview_Project')
import analysis_logic

folder_path = r'D:\ex_work\AirQualityReview_Project\data\csv_main\C'
setpoint_path = r'D:\ex_work\AirQualityReview_Project\data\SetPointLimit.xlsx'

# Check what dates are actually in the 1-P040 CSV file
f_path = os.path.join(folder_path, '1-P040_05-14-26_01-00.csv')
print('=== Checking 1-P040 CSV content (first 15 data rows) ===')
with open(f_path, 'r') as f:
    lines = f.readlines()

# Show first 15 lines
for i in range(min(15, len(lines))):
    print(f'Line {i}: {lines[i].strip()[:120]}')
print()

# Parse and show actual data dates
setpoint_df = pd.read_excel(setpoint_path)
df = analysis_logic.prepare_df(f_path, '1-P040', setpoint_df)
print(f'Total rows parsed: {len(df)}')
print(f'Date range in data: {df["DateTime"].min()} to {df["DateTime"].max()}')
print()
print('First 10 rows:')
print(df[['DateTime','Temperature','Humidity','Pressure']].head(10).to_string())
print()
print('Temperature stats:')
print(df['Temperature'].describe())
print()

# Check what happens with analyze_files filtered to 2026-05-13
print('=== Now checking analyze_files with start=2026-05-13, end=2026-05-13 ===')
out_path, logs, plot = analysis_logic.analyze_files(
    folder_path=folder_path,
    setpoint_path=setpoint_path,
    selected_rooms=['1-P040', '1-P051'],
    start_date='2026-05-13',
    end_date='2026-05-13'
)
print(f'Output path: {out_path}')
print(f'Plot result type: {type(plot)}')
if isinstance(plot, dict):
    print(f'Keys: {list(plot.keys())}')
    if 'summary' in plot:
        print(f'Summary: {plot["summary"]}')
    if 'violation_intervals' in plot:
        print(f'Violation intervals: {len(plot.get("violation_intervals", []))}')
        for v in plot.get("violation_intervals", []):
            print(f'  {v}')
    if 'stats' in plot:
        print(f'Stats: {plot["stats"]}')