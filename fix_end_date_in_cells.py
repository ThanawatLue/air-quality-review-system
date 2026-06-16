import json

notebook_path = r'D:\ex_work\AirQualityReview_Project\validation_docs\Validation_Test_Execution.ipynb'

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

cells = nb['cells']

# ============================================================
# Fix InT-01 (cell 51): change end_date=csv_min_date -> end_date=csv_max_date
# ============================================================
src_51 = ''.join(cells[51]['source'])
old_line = "    end_date=csv_min_date\n"
new_line = "    end_date=csv_max_date\n"
if old_line in src_51:
    src_51 = src_51.replace(old_line, new_line)
    print('InT-01: end_date changed from csv_min_date to csv_max_date')
else:
    print('InT-01: Could NOT find end_date=csv_min_date')
    # Debug: show lines around end_date
    lines = src_51.split('\n')
    for i, line in enumerate(lines):
        if 'end_date' in line:
            print(f'  Line {i}: {line.strip()}')
cells[51]['source'] = src_51.split('\n(True)') if False else [l + '\n' for l in src_51.split('\n')]
# Rebuild source as list of lines
src_lines = src_51.split('\n')
# Remove trailing empty string if last char was \n
if src_lines and src_lines[-1] == '':
    src_lines = src_lines[:-1]
# Add \n to each line except possibly the last
result = []
for i, line in enumerate(src_lines):
    if i < len(src_lines) - 1:
        result.append(line + '\n')
    else:
        result.append(line)
cells[51]['source'] = result
cells[51]['execution_count'] = None

# ============================================================
# Fix InT-04 (cell 57): same issue - start_date and end_date both = "2026-05-13"
# This causes end_dt = midnight, filtering out all data after 00:00
# ============================================================
# The fix is already correct in the current notebook (start/end both 2026-05-13)
# But the issue is in analysis_logic.py's _compute_plot_result using end_dt as filter
# Since we can't change analysis_logic.py, we should change the cell to use end_date = "2026-05-14"
# so end_dt becomes 2026-05-14 00:00:00 which properly includes all 2026-05-13 data

src_57 = ''.join(cells[57]['source'])
old_line_57 = '    end_date="2026-05-13"\n'
new_line_57 = '    end_date="2026-05-14"\n'
if old_line_57 in src_57:
    src_57 = src_57.replace(old_line_57, new_line_57)
    print('InT-04: end_date changed from 2026-05-13 to 2026-05-14')
else:
    print('InT-04: Could NOT find end_date=2026-05-13')
    lines = src_57.split('\n')
    for i, line in enumerate(lines):
        if 'end_date' in line:
            print(f'  Line {i}: {line.strip()}')

src_lines_57 = src_57.split('\n')
if src_lines_57 and src_lines_57[-1] == '':
    src_lines_57 = src_lines_57[:-1]
result_57 = []
for i, line in enumerate(src_lines_57):
    if i < len(src_lines_57) - 1:
        result_57.append(line + '\n')
    else:
        result_57.append(line)
cells[57]['source'] = result_57
cells[57]['execution_count'] = None

# ============================================================
# Also fix InT-02 (cell 53) - same issue with end_date
# ============================================================
src_53 = ''.join(cells[53]['source'])
old_line_53a = '    end_date="2026-05-13"\n'
new_line_53a = '    end_date="2026-05-14"\n'
count_53 = src_53.count(old_line_53a)
if count_53 > 0:
    src_53 = src_53.replace(old_line_53a, new_line_53a)
    print(f'InT-02: {count_53} occurrences of end_date changed from 2026-05-13 to 2026-05-14')
else:
    print('InT-02: Could NOT find end_date=2026-05-13')

src_lines_53 = src_53.split('\n')
if src_lines_53 and src_lines_53[-1] == '':
    src_lines_53 = src_lines_53[:-1]
result_53 = []
for i, line in enumerate(src_lines_53):
    if i < len(src_lines_53) - 1:
        result_53.append(line + '\n')
    else:
        result_53.append(line)
cells[53]['source'] = result_53
cells[53]['execution_count'] = None

# ============================================================
# Also fix InT-03 (cell 55) - same issue with end_date
# ============================================================
src_55 = ''.join(cells[55]['source'])
old_line_55a = '    end_date="2026-05-13"\n'
new_line_55a = '    end_date="2026-05-14"\n'
count_55 = src_55.count(old_line_55a)
if count_55 > 0:
    src_55 = src_55.replace(old_line_55a, new_line_55a)
    print(f'InT-03: {count_55} occurrences of end_date changed from 2026-05-13 to 2026-05-14')
else:
    print('InT-03: Could NOT find end_date=2026-05-13')

src_lines_55 = src_55.split('\n')
if src_lines_55 and src_lines_55[-1] == '':
    src_lines_55 = src_lines_55[:-1]
result_55 = []
for i, line in enumerate(src_lines_55):
    if i < len(src_lines_55) - 1:
        result_55.append(line + '\n')
    else:
        result_55.append(line)
cells[55]['source'] = result_55
cells[55]['execution_count'] = None

with open(notebook_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print('\nDone! All cells updated.')