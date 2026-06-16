import os
import json

recovered_dir = r"D:\ex_work\AirQualityReview_Project\scratch\recovered_notebooks"
if os.path.exists(recovered_dir):
    for f_name in os.listdir(recovered_dir):
        if f_name.endswith('.ipynb'):
            f_path = os.path.join(recovered_dir, f_name)
            try:
                with open(f_path, 'r', encoding='utf-8') as f:
                    nb = json.load(f)
                # Check cells
                for idx, cell in enumerate(nb['cells']):
                    if cell['cell_type'] == 'code':
                        src = ''.join(cell['source'])
                        if 'InT-05: analyze_files' in src:
                            print(f"File {f_name}, Cell {idx} contains 'InT-05: analyze_files'")
                            # Print first 10 lines of this cell
                            print('\n'.join(cell['source'][:10]))
                            print("="*40)
            except Exception as e:
                print(f"Error reading {f_name}: {e}")
