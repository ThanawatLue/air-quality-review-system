import json

with open(r'D:\ex_work\AirQualityReview_Project\scratch\recovered_notebooks\notebook_cc1522ed.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

with open(r'D:\ex_work\AirQualityReview_Project\scratch\cc1522ed_int_cells.txt', 'w', encoding='utf-8') as outf:
    for idx in range(50, 62):
        if idx >= len(nb['cells']):
            break
        cell = nb['cells'][idx]
        outf.write(f"=== Cell {idx} ({cell['cell_type']}) ===\n")
        outf.write(''.join(cell['source']))
        outf.write("\n" + "="*80 + "\n\n")
