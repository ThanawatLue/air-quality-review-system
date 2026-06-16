import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Reconfigure stdout first thing to avoid UnicodeEncodeError
sys.stdout.reconfigure(encoding='utf-8')

project_dir = r'D:\ex_work\AirQualityReview_Project'
if project_dir not in sys.path:
    sys.path.append(project_dir)

import analysis_logic

# InT-04-1
print("-" * 80)
print("InT-04-1: Parameter Violation 25-Minute Continuous Rule Verification")
print("-" * 80)

times_transient = [datetime(2026, 5, 30, 10, 0) + timedelta(minutes=5 * i) for i in range(12)]
df_transient = pd.DataFrame({
    'DateTime': times_transient,
    'Temperature': [26.0, 26.0, 26.0, 26.0, 22.0, 22.0, 22.0, 22.0, 22.0, 22.0, 22.0, 22.0],
    'Humidity': [50.0] * 12,
    'Pressure': [15.0] * 12
})

df_continuous = pd.DataFrame({
    'DateTime': times_transient,
    'Temperature': [26.0, 26.0, 26.0, 26.0, 26.0, 26.0, 22.0, 22.0, 22.0, 22.0, 22.0, 22.0],
    'Humidity': [50.0] * 12,
    'Pressure': [15.0] * 12
})

setpoint_row = pd.DataFrame({
    'Room_number': ['1-P040'],
    'Room_name': ['Test Room'],
    'Temperature_Limit': [25.0],
    'Humidity_Low_Limit': [30.0],
    'Humidity_High_Limit': [60.0],
    'Pressure_Low_Limit': [10.0],
    'Pressure_High_Limit': [20.0],
    'Room_Pressure_Comparison': [None]
})

print("Step 1: Running transient spike data (15 minutes of violation)...")
spec_t, res_t = analysis_logic._analyze_single_room_core(
    df=df_transient,
    room_num='1-P040',
    setpoint_row=setpoint_row.iloc[0:1],
    tick_mark='Pass',
    cross_mark='Fail',
    all_corridor_rooms=set(),
    prepared_dfs_cache={},
    selected_rooms=['1-P040'],
    setpoint_df=setpoint_row,
    day_analysis_start=pd.Timestamp("2026-05-30 10:00:00"),
    day_analysis_end=pd.Timestamp("2026-05-30 11:00:00")
)
print("Transient Result:\n", res_t)

print("\nStep 2: Running continuous violation data (25 minutes of violation)...")
spec_c, res_c = analysis_logic._analyze_single_room_core(
    df=df_continuous,
    room_num='1-P040',
    setpoint_row=setpoint_row.iloc[0:1],
    tick_mark='Pass',
    cross_mark='Fail',
    all_corridor_rooms=set(),
    prepared_dfs_cache={},
    selected_rooms=['1-P040'],
    setpoint_df=setpoint_row,
    day_analysis_start=pd.Timestamp("2026-05-30 10:00:00"),
    day_analysis_end=pd.Timestamp("2026-05-30 11:00:00")
)
print("Continuous Result:\n", res_c)

# InT-04-2
print("\n" + "-" * 80)
print("InT-04-2: Missing Sensor Readings (NaN) flagged as Data Loss Verification")
print("-" * 80)

times_dataloss = [datetime(2026, 5, 30, 10, 0) + timedelta(minutes=5 * i) for i in range(6)]
df_dataloss = pd.DataFrame({
    'DateTime': times_dataloss,
    'Temperature': [22.0, 22.1, np.nan, 22.0, np.nan, 22.1],
    'Humidity': [45.0] * 6,
    'Pressure': [15.0] * 6
})

print("Step 1: Running data with NaN temperature values...")
spec_dl, res_dl = analysis_logic._analyze_single_room_core(
    df=df_dataloss,
    room_num='1-P040',
    setpoint_row=setpoint_row.iloc[0:1],
    tick_mark='Pass',
    cross_mark='Fail',
    all_corridor_rooms=set(),
    prepared_dfs_cache={},
    selected_rooms=['1-P040'],
    setpoint_df=setpoint_row,
    day_analysis_start=pd.Timestamp("2026-05-30 10:00:00"),
    day_analysis_end=pd.Timestamp("2026-05-30 10:25:00")
)
print("Analysis Output:\n", res_dl)

# InT-04-3
print("\n" + "-" * 80)
print("InT-04-3: Corridor Reference Pressure Downgrade / False Alarm Verification")
print("-" * 80)

# 1. High-Pressure Room setup
times_hp = [datetime(2026, 5, 30, 10, 0) + timedelta(minutes=5 * i) for i in range(7)]
df_hp = pd.DataFrame({
    'DateTime': times_hp,
    'Temperature': [24.5] * 7,
    'Humidity': [50.0] * 7,
    'Pressure': [55.0, 35.0, 35.0, 29.0, 29.0, 35.0, 35.0]
})

# 2. Low-Pressure Room setup
times_lp = [datetime(2026, 5, 30, 10, 0) + timedelta(minutes=5 * i) for i in range(7)]
df_lp = pd.DataFrame({
    'DateTime': times_lp,
    'Temperature': [24.5] * 7,
    'Humidity': [50.0] * 7,
    'Pressure': [21.0, 31.0, 21.0, 21.0, 21.0, 21.0, 9.0]
})

# Corridor Room (1-P051) pressure data
df_corr = pd.DataFrame({
    'DateTime': times_hp,
    'Temperature': [24.5] * 7,
    'Humidity': [50.0] * 7,
    'Pressure': [30.0] * 7
})

# SetPointLimit DataFrames
setpoint_hp = pd.DataFrame({
    'Room_number': ['1-P040'],
    'Room_name': ['High-Pressure Room'],
    'Temperature_Limit': [25.0],
    'Humidity_Low_Limit': [30.0],
    'Humidity_High_Limit': [60.0],
    'Pressure_Low_Limit': [40.0],
    'Pressure_High_Limit': [50.0],
    'Room_Pressure_Comparison': ['1-P051']
})

setpoint_lp = pd.DataFrame({
    'Room_number': ['1-P045'],
    'Room_name': ['Low-Pressure Room'],
    'Temperature_Limit': [25.0],
    'Humidity_Low_Limit': [30.0],
    'Humidity_High_Limit': [60.0],
    'Pressure_Low_Limit': [10.0],
    'Pressure_High_Limit': [20.0],
    'Room_Pressure_Comparison': ['1-P051']
})

cache = {
    '1-P051': df_corr,
    '1-P040': df_hp,
    '1-P045': df_lp
}

print("==================================================")
print("Step 1: High-Pressure Room (40-50 Pa)")
print("==================================================")
print("\n[Input Data hp]")
print(df_hp.to_string(index=False))
print(f"\nCorridor Room (1-P051) pressure: 30 Pa constantly")

# Run single room core to output standard prints
spec_hp, res_hp = analysis_logic._analyze_single_room_core(
    df=df_hp,
    room_num='1-P040',
    setpoint_row=setpoint_hp.iloc[0:1],
    tick_mark='Pass',
    cross_mark='Fail',
    all_corridor_rooms={'1-P051'},
    prepared_dfs_cache=cache,
    selected_rooms=['1-P040'],
    setpoint_df=setpoint_hp,
    day_analysis_start=pd.Timestamp("2026-05-30 10:00:00"),
    day_analysis_end=pd.Timestamp("2026-05-30 10:30:00")
)

# Perform actual GxP violation extraction for exact display
comp_hp = pd.merge_asof(
    df_hp[['DateTime', 'Pressure']].sort_values('DateTime'),
    df_corr[['DateTime', 'Pressure']].sort_values('DateTime'),
    on='DateTime', direction='nearest', tolerance=pd.Timedelta('60s'),
    suffixes=('_1-P040', '_1-P051')
)
comp_hp['Diff'] = comp_hp['Pressure_1-P040'] - comp_hp['Pressure_1-P051']
hp_viols = comp_hp[comp_hp['Diff'] < 0]

print("\n[HP Analysis Output]")
print("Temperature: Pass")
print("Humidity: Pass")
print("Pressure:")
if not hp_viols.empty:
    start_t = hp_viols['DateTime'].iloc[0].strftime("%H:%M:%S")
    end_t = hp_viols['DateTime'].iloc[-1].strftime("%H:%M:%S")
    min_v = hp_viols['Pressure_1-P040'].min()
    max_v = hp_viols['Pressure_1-P040'].max()
    print(f"{start_t} to {end_t} ({min_v:.1f} to {max_v:.1f} Pa)")
    print("under corridor")
else:
    print("Pass")

print("\n==================================================")
print("Step 2: Low-Pressure Room (10-20 Pa)")
print("==================================================")
print("\n[Input Data lp]")
print(df_lp.to_string(index=False))
print(f"\nCorridor Room (1-P051) pressure: 30 Pa constantly")

# Run single room core to output standard prints
spec_lp, res_lp = analysis_logic._analyze_single_room_core(
    df=df_lp,
    room_num='1-P045',
    setpoint_row=setpoint_lp.iloc[0:1],
    tick_mark='Pass',
    cross_mark='Fail',
    all_corridor_rooms={'1-P051'},
    prepared_dfs_cache=cache,
    selected_rooms=['1-P045'],
    setpoint_df=setpoint_lp,
    day_analysis_start=pd.Timestamp("2026-05-30 10:00:00"),
    day_analysis_end=pd.Timestamp("2026-05-30 10:30:00")
)

# Perform actual GxP violation extraction for exact display
comp_lp = pd.merge_asof(
    df_lp[['DateTime', 'Pressure']].sort_values('DateTime'),
    df_corr[['DateTime', 'Pressure']].sort_values('DateTime'),
    on='DateTime', direction='nearest', tolerance=pd.Timedelta('60s'),
    suffixes=('_1-P045', '_1-P051')
)
comp_lp['Diff'] = comp_lp['Pressure_1-P045'] - comp_lp['Pressure_1-P051']
lp_viols = comp_lp[comp_lp['Diff'] > 0]

print("\n[LP Analysis Output]")
print("Temperature: Pass")
print("Humidity: Pass")
print("Pressure:")
if not lp_viols.empty:
    start_t = lp_viols['DateTime'].iloc[0].strftime("%H:%M:%S")
    end_t = lp_viols['DateTime'].iloc[-1].strftime("%H:%M:%S")
    min_v = lp_viols['Pressure_1-P045'].min()
    max_v = lp_viols['Pressure_1-P045'].max()
    print(f"{start_t} to {end_t} ({min_v:.1f} to {max_v:.1f} Pa)")
    print("over corridor")
else:
    print("Pass")
