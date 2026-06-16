import os
import json

project_dir = r"D:\ex_work\AirQualityReview_Project"

for root, dirs, files in os.walk(project_dir):
    for f_name in files:
        if f_name.endswith('.ipynb'):
            f_path = os.path.join(root, f_name)
            try:
                with open(f_path, 'r', encoding='utf-8') as f:
                    nb = json.load(f)
                for idx, cell in enumerate(nb['cells']):
                    if cell['cell_type'] == 'code':
                        src = ''.join(cell['source'])
                        if 'Phase I full statistical execution directly on real data' in src:
                            print(f"FOUND in {f_path}, Cell {idx}")
                            print(''.join(cell['source'][:15]))
                            print("="*50)
            except Exception as e:
                pass
