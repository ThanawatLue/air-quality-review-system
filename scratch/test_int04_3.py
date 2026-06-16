import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

project_dir = r'D:\ex_work\AirQualityReview_Project'
if project_dir not in sys.path:
    sys.path.append(project_dir)

import analysis_logic

# Set up the inputs for High-Pressure Room (40-50 Pa)
times_hp = [datetime(2026, 5, 30, 10, 0) + timedelta(minutes=5 * i) for i in range(7)]
df_hp = pd.DataFrame({
    'DateTime': times_hp,
    'Temperature': [24.5] * 7,
    'Humidity': [50.0] * 7,
    'Pressure': [55.0, 35.0, 35.0, 29.0, 29.0, 35.0, 35.0]
})

# Set up the inputs for Low-Pressure Room (10-20 Pa)
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

# We register the corridor dataframe cache
cache = {
    '1-P051': df_corr,
    '1-P040': df_hp,
    '1-P045': df_lp
}

sys.stdout.reconfigure(encoding='utf-8')

print("Step 1: Analyzing High-Pressure Room (1-P040)...")
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

print("\n--- High-Pressure Room Analysis Result Summary ---")
print(res_hp)

print("\nStep 2: Analyzing Low-Pressure Room (1-P045)...")
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

print("\n--- Low-Pressure Room Analysis Result Summary ---")
print(res_lp)
