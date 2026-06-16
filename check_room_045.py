import os, pandas as pd
import sys
sys.path.append(r'D:\ex_work\AirQualityReview_Project')
import analysis_logic

folder_path = r'D:\ex_work\AirQualityReview_Project\data\csv_main\C'
files = os.listdir(folder_path)

# Check 1-P045 files
matches = [f for f in files if f.startswith('1-P045')]
print('1-P045 files:', len(matches))
for f in matches:
    print('  ' + f)

# Also check 1-P051 still available
matches2 = [f for f in files if f.startswith('1-P051')]
print('1-P051 files:', len(matches2))
for f in matches2:
    print('  ' + f)

# Inspect 1-P045 CSV structure
if matches:
    fpath = os.path.join(folder_path, matches[0])
    with open(fpath, 'r') as f:
        lines = f.readlines()
    print('\n1-P045 first 15 lines:')
    for i, line in enumerate(lines[:15]):
        print('  ' + str(i) + ': ' + line.strip()[:120])
    print('  ... total ' + str(len(lines)) + ' lines')

# Load SetPointLimit to check 1-P045
setpoint_df = pd.read_excel(r'D:\ex_work\AirQualityReview_Project\data\SetPointLimit.xlsx')
sp045 = setpoint_df[setpoint_df['Room_number'].str.strip() == '1-P045']
print('\n1-P045 specs:')
print('  Room_name: ' + str(sp045['Room_name'].iloc[0]))
print('  Temp_Limit: ' + str(sp045['Temperature_Limit'].iloc[0]))
print('  Humidity: ' + str(sp045['Humidity_Low_Limit'].iloc[0]) + '-' + str(sp045['Humidity_High_Limit'].iloc[0]))
print('  Pressure: ' + str(sp045['Pressure_Low_Limit'].iloc[0]) + '-' + str(sp045['Pressure_High_Limit'].iloc[0]))
print('  Corridor: ' + str(sp045['Room_Pressure_Comparison'].iloc[0]))

# Parse the CSV and show what data is available
if matches:
    fpath = os.path.join(folder_path, matches[0])
    df = analysis_logic.prepare_df(fpath, '1-P045', setpoint_df)
    print('\n1-P045 parsed data:')
    print('  Rows: ' + str(len(df)))
    print('  Date range: ' + str(df['DateTime'].min()) + ' to ' + str(df['DateTime'].max()))
    print('  Temperature range: ' + str(df['Temperature'].min()) + ' to ' + str(df['Temperature'].max()))
    print(df[['DateTime','Temperature','Humidity','Pressure']].head(10).to_string())