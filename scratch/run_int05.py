import json
import sys
import os

nb_path = r'D:\ex_work\AirQualityReview_Project\validation_docs\Validation_Test_Execution.ipynb'
sys.path.insert(0, r'D:\ex_work\AirQualityReview_Project')

with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

cell = nb['cells'][59]
code = ''.join(cell['source'])

print("Executing InT-05:")
exec(code, globals())
