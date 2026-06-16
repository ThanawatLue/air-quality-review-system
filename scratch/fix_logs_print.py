import json

nb_path = r'D:\ex_work\AirQualityReview_Project\validation_docs\Validation_Test_Execution.ipynb'

with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# The cells we want to modify to print full logs are 51, 59, 61
target_cells = [51, 59, 61]

for idx in target_cells:
    cell = nb['cells'][idx]
    new_source = []
    for line in cell['source']:
        # Replace logs[:4000] with logs
        if 'print(logs[:4000]' in line:
            line = line.replace('print(logs[:4000]', 'print(logs')
        new_source.append(line)
    cell['source'] = new_source

with open(nb_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print("Successfully replaced print(logs[:4000]) with print(logs) in the notebook.")
