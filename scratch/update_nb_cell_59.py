import json

nb_path = r'D:\ex_work\AirQualityReview_Project\validation_docs\Validation_Test_Execution.ipynb'

with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

cell = nb['cells'][59]

new_source = []
for line in cell['source']:
    if 'before = Path(analysis_logic.audit_trail.LOG_FILE)' in line:
        new_source.extend([
            '# Ensure a realistic valid file for room 1-P045 on 2026-05-14 exists\n',
            'valid_path = BAS_SOURCE / "1-P045_05-15-26_01-00.csv"\n',
            'if not valid_path.exists():\n',
            '    import random\n',
            '    random.seed(12345)\n',
            '    lines = [\n',
            '        "Key            Name:Suffix                                Trend Definitions Used,,,,\\n",\n',
            '        "Point_1:,1A052-25_1-P045 ROOM TEMP,,5 minutes,\\n",\n',
            '        "Point_2:,1A052-26_1-P045 ROOM HUM,,5 minutes,\\n",\n',
            '        "Point_3:,1A052-27_1-P045 ROOM PRES,,5 minutes,\\n",\n',
            '        "Time Interval:,5 Minutes,,,\\n",\n',
            '        "Date Range:,5/14/2026 00:00:00 - 5/14/2026 23:59:59,,,\\n",\n',
            '        "Report Timings:,All Hours,,,\\n",\n',
            '        ",,,,\\n",\n',
            '        "<>Date,Time,Point_1,Point_2,Point_3\\n"\n',
            '    ]\n',
            '    for hour in range(24):\n',
            '        for minute in range(0, 60, 5):\n',
            '            time_str = f"{hour:02d}:{minute:02d}:00"\n',
            '            temp = round(21.5 + random.uniform(-0.3, 0.3), 1)\n',
            '            hum = round(37.5 + random.uniform(-0.7, 0.7), 1)\n',
            '            pres = round(15.0 + random.uniform(-0.8, 0.8), 1)\n',
            '            lines.append(f"5/14/2026,{time_str},{temp},{hum},{pres}\\n")\n',
            '    lines.append(" ******************************** End of Report *********************************,,,\\n")\n',
            '    valid_path.write_text("".join(lines), encoding="utf-8")\n',
            '\n'
        ])
    new_source.append(line)

cell['source'] = new_source

with open(nb_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print("Successfully updated cell 59 in notebook.")
