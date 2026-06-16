import json

nb_path = r'D:\ex_work\AirQualityReview_Project\validation_docs\Validation_Test_Execution.ipynb'

with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

target_cells = [51, 53, 55, 57, 59, 61]
changed = False

for idx in target_cells:
    cell = nb['cells'][idx]
    new_source = []
    for line in cell['source']:
        if 'print(logs[:4000]' in line:
            print(f"Replacing logs[:4000] in Cell {idx}")
            line = line.replace('print(logs[:4000]', 'print(logs')
            changed = True
        new_source.append(line)
    cell['source'] = new_source

if changed:
    with open(nb_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1)
    print("Saved notebook with replacements.")
else:
    print("No print(logs[:4000]) was found in target cells!")
