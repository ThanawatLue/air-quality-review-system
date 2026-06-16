import json
import sys
import os

nb_path = r'D:\ex_work\AirQualityReview_Project\validation_docs\Validation_Test_Execution.ipynb'

# Put workspace directory in system path so we can import modules
sys.path.insert(0, r'D:\ex_work\AirQualityReview_Project')

with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# The cells we want to execute are 51, 53, 55, 57, 59, 61
target_cells = [51, 53, 55, 57, 59, 61]

for idx in target_cells:
    cell = nb['cells'][idx]
    code = ''.join(cell['source'])
    print(f"\n==================================================")
    print(f"RUNNING CELL {idx} (InT-0{int((idx-49)/2)})")
    print(f"==================================================")
    try:
        exec(code, globals())
        print(f"CELL {idx} PASSED!")
    except Exception as e:
        print(f"CELL {idx} FAILED: {e}")
        import traceback
        traceback.print_exc()
