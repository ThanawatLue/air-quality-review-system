import sys
sys.path.append(r'D:\ex_work\AirQualityReview_Project')
import analysis_logic

file_path = r'D:\ex_work\AirQualityReview_Project\data\csv_main\C\1-P045_05-15-26_01-00.csv'
start, end = analysis_logic.get_file_date_range(file_path)
print("Start:", start)
print("End:", end)

# Also let's run parse_filename_for_datetime
fname = '1-P045_05-15-26_01-00.csv'
dt = analysis_logic.parse_filename_for_datetime(fname)
print("Parsed filename datetime:", dt)
