import json

with open(r'D:\ex_work\AirQualityReview_Project\validation_docs\Validation_Test_Execution.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

with open(r'D:\ex_work\AirQualityReview_Project\scratch\active_int_cells.txt', 'w', encoding='utf-8') as outf:
    for idx in range(50, 63):
        if idx >= len(nb['cells']):
            break
        cell = nb['cells'][idx]
        outf.write(f"=== Cell {idx} ({cell['cell_type']}) ===\n")
        outf.write(''.join(cell['source']))
        outf.write("\n" + "="*80 + "\n\n")
