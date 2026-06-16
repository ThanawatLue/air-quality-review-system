import sys
import pandas as pd
sys.path.append(r'D:\ex_work\AirQualityReview_Project')
import analysis_logic

folder_path = r'D:\ex_work\AirQualityReview_Project\data\csv_b10'
setpoint_path = r'D:\ex_work\AirQualityReview_Project\data\SetPointLimit_B10.xlsx'
selected_rooms = ["10-1-096", "10-1-097", "10-1-098"]

setpoint_df = pd.read_excel(setpoint_path)
_, df, sensors = analysis_logic.prepare_df_phase2(folder_path, '10-1-096', setpoint_df)

day_start = pd.Timestamp('2026-05-13 00:00:00')
day_end = pd.Timestamp('2026-05-13 23:55:00')

day_df = df[(df['DateTime'] >= day_start) & (df['DateTime'] <= day_end)].copy().reset_index(drop=True)
setpoint_row = setpoint_df[setpoint_df['Room_number'].astype(str) == '10-1-096']

# Trace _analyze_single_room_core variables
T_lim = float(setpoint_row['Temperature_Limit'].iloc[0])
t_df_all = day_df[day_df['Temperature'] > T_lim]

print("T_lim:", T_lim)
print("t_df_all length:", len(t_df_all))

if len(t_df_all) > 0:
    diffs = t_df_all['DateTime'].diff(5)
    print("Diffs sample:")
    print(diffs.head(10))
    t_25 = t_df_all[t_df_all['DateTime'].diff(5).dt.total_seconds() == 1500]
    print("t_25 length:", len(t_25))
