import os
import glob
import shutil

src_dir = r'D:\ex_work\gpo_AirQualityReview_Project\data\B16_2026-06-26\CSV 30-6-2026'
base_dir = r'D:\ex_work\gpo_AirQualityReview_Project\data\B16_2026-06-26'

new_files = glob.glob(os.path.join(src_dir, '*.Csv'))
replaced = 0

for nf in new_files:
    fname = os.path.basename(nf)
    room_id = fname.split('_')[0]
    data_type = fname.split('_')[1]
    
    target_dirs = glob.glob(os.path.join(base_dir, '**', room_id, 'Raw Data'), recursive=True)
    if target_dirs:
        target_dir = target_dirs[0]
        old_files = list(set(glob.glob(os.path.join(target_dir, f'{room_id}_{data_type}_*.csv')) + glob.glob(os.path.join(target_dir, f'{room_id}_{data_type}_*.Csv'))))
        for oldf in old_files:
            os.remove(oldf)
        
        # Copy new file
        shutil.copy(nf, os.path.join(target_dir, fname))
        replaced += 1

print(f'Replaced {replaced} files successfully.')
