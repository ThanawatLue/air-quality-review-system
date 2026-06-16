import json

with open(r'D:\ex_work\AirQualityReview_Project\scratch\recovered_notebooks\notebook_5debabf8.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

for idx, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'markdown':
        src = ''.join(cell['source'])
        if 'InT-' in src or 'Integration' in src:
            print(f"=== Cell {idx} ({cell['cell_type']}) ===")
            print(src.strip())
            print("=" * 40)
            if idx + 1 < len(nb['cells']):
                next_cell = nb['cells'][idx + 1]
                print(f"=== Cell {idx+1} ({next_cell['cell_type']}) ===")
                print(''.join(next_cell['source']))
                print("=" * 40)
