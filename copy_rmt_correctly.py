import os
import glob
import shutil

source_dir = r"D:\ex_work\gpo_AirQualityReview_Project\data\B16_2026-06-26\CSV 30-6-2026"
target_base_dir = r"D:\ex_work\gpo_AirQualityReview_Project\data\B16_2026-06-26"

# Get all new RMT files
new_rmt_files = glob.glob(os.path.join(source_dir, "*_RMT_*.csv"), recursive=False)
if not new_rmt_files:
    new_rmt_files = glob.glob(os.path.join(source_dir, "*_RMT_*.Csv"), recursive=False)

success_count = 0
for new_file in new_rmt_files:
    filename = os.path.basename(new_file)
    room_name = filename.split("_RMT_")[0]
    
    search_pattern = os.path.join(target_base_dir, "*", room_name, "Raw Data")
    matched_dirs = glob.glob(search_pattern)
    
    if matched_dirs:
        target_dir = matched_dirs[0]
        
        # Use set to avoid duplicates due to case-insensitivity on Windows
        old_rmt_files = set(glob.glob(os.path.join(target_dir, "*_RMT_*.csv")) + glob.glob(os.path.join(target_dir, "*_RMT_*.Csv")))
        for old_file in old_rmt_files:
            try:
                os.remove(old_file)
                print(f"Removed old file: {os.path.basename(old_file)}")
            except FileNotFoundError:
                pass
            
        shutil.copy2(new_file, target_dir)
        success_count += 1

print(f"Successfully replaced {success_count} RMT files.")
