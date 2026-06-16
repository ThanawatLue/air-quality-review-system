import json

with open(r'D:\ex_work\AirQualityReview_Project\validation_docs\Validation_Test_Execution.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

for idx in range(49, 63):
    if idx >= len(nb['cells']):
        break
    cell = nb['cells'][idx]
    print(f"=== Cell {idx} ({cell['cell_type']}) ===")
    print(''.join(cell['source']))
    print("=" * 40)
