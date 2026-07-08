import analysis_logic
import os

raw_data_path = r'D:\ex_work\gpo_AirQualityReview_Project\data\B16_2026-06-26'
setpoint_file = r'D:\ex_work\gpo_AirQualityReview_Project\data\SetPointLimit_B16.xlsx'

print('Running phase 2 analysis...')
output, summary, rooms = analysis_logic.analyze_files_phase2(raw_data_path, setpoint_file)

out_file = r'D:\ex_work\gpo_AirQualityReview_Project\data\AQR_Report_P2_B16_Final_Test.xlsx'
with open(out_file, 'wb') as f:
    f.write(output)

print(f'Report generated successfully! Saved to {out_file}')
