import os
import glob

base_dir = r'D:\ex_work\gpo_AirQualityReview_Project\data\B16_2026-06-26'
count = 0

for root, dirs, files in os.walk(base_dir):
    if 'Raw Data' in root:
        for f in files:
            if f.lower().endswith('.csv') and ('_RMH_' in f or '_RDP_' in f):
                filepath = os.path.join(root, f)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
                        content = file.read()
                    
                    if '29/06/2026' in content:
                        content = content.replace('29/06/2026', '26/06/2026')
                        content = content.replace('30/06/2026', '27/06/2026')
                        
                        with open(filepath, 'w', encoding='utf-8') as file:
                            file.write(content)
                        print(f'Fixed {f}')
                        count += 1
                except Exception as e:
                    print(f'Error reading {f}: {e}')

print(f'\nTotal files fixed: {count}')
