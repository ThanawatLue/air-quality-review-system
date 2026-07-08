import pandas as pd
import json
import re

# 1. Parse Markdown Table
with open('C:/Users/thana/.gemini/antigravity/brain/7345c94d-547a-49f7-97a8-e9faccd8f4ab/.system_generated/tasks/task-4.log', 'r', encoding='utf-8') as f:
    log_data = json.load(f)

markdown_text = log_data['markdown']
lines = markdown_text.split('\n')

parsed_data = {}
for line in lines:
    line = line.strip()
    if not line.startswith('|'): continue
    cols = [c.strip() for c in line.split('|')]
    if len(cols) >= 19:
        try:
            item_no_str = cols[1]
            if not item_no_str.isdigit(): continue
            
            room_no = cols[4].strip()
            if room_no in parsed_data:
                continue
                
            def extract_num(s):
                match = re.search(r'[\d\.]+', s)
                return float(match.group()) if match else None

            temp_limit = extract_num(cols[12])  # Temp action high
            hum_low_raw = cols[13]
            hum_low = extract_num(hum_low_raw) if hum_low_raw != 'N/A' else None
            hum_high = extract_num(cols[15])
            pres_low = extract_num(cols[16])
            pres_high = extract_num(cols[18])
            
            parsed_data[room_no] = {
                'Room_name': cols[5],
                'Temperature_Limit': temp_limit,
                'Humidity_Low_Limit': hum_low,
                'Humidity_High_Limit': hum_high,
                'Pressure_Low_Limit': pres_low,
                'Pressure_High_Limit': pres_high
            }
        except Exception as e:
            pass

# 2. Compare with Excel & Apply Changes
df = pd.read_excel('D:/ex_work/gpo_AirQualityReview_Project/data/SetPointLimit_B10.xlsx')
diffs_urs = []
diffs_zero = []

for idx, row in df.iterrows():
    room_no = str(row['Room_number']).strip()
    
    # 2.1 Apply URS changes
    if room_no in parsed_data:
        new_vals = parsed_data[room_no]
        changes = {}
        
        def check_diff(col, new_val):
            old_val = row[col]
            if pd.isna(old_val) and new_val is None: return False
            if pd.isna(old_val) and new_val is not None:
                changes[col] = (old_val, new_val)
                df.at[idx, col] = new_val
                return True
            elif not pd.isna(old_val) and new_val is None:
                changes[col] = (old_val, new_val)
                df.at[idx, col] = new_val
                return True
            elif abs(old_val - new_val) > 0.001:
                changes[col] = (old_val, new_val)
                df.at[idx, col] = new_val
                return True
            return False

        check_diff('Temperature_Limit', new_vals['Temperature_Limit'])
        check_diff('Humidity_Low_Limit', new_vals['Humidity_Low_Limit'])
        check_diff('Humidity_High_Limit', new_vals['Humidity_High_Limit'])
        check_diff('Pressure_Low_Limit', new_vals['Pressure_Low_Limit'])
        check_diff('Pressure_High_Limit', new_vals['Pressure_High_Limit'])
        
        if changes:
            diffs_urs.append((room_no, row['Room_name'], changes))
            
    # 2.2 Apply the "High limit exists but Low limit is empty -> 0" rule
    zero_changes = {}
    
    # Humidity
    h_high = df.at[idx, 'Humidity_High_Limit']
    h_low = df.at[idx, 'Humidity_Low_Limit']
    if pd.notna(h_high) and pd.isna(h_low):
        zero_changes['Humidity_Low_Limit'] = (h_low, 0.0)
        df.at[idx, 'Humidity_Low_Limit'] = 0.0
        
    # Pressure
    p_high = df.at[idx, 'Pressure_High_Limit']
    p_low = df.at[idx, 'Pressure_Low_Limit']
    if pd.notna(p_high) and pd.isna(p_low):
        zero_changes['Pressure_Low_Limit'] = (p_low, 0.0)
        df.at[idx, 'Pressure_Low_Limit'] = 0.0
        
    if zero_changes:
        diffs_zero.append((room_no, row['Room_name'], zero_changes))

print(f"Total URS differences applied: {len(diffs_urs)}")
print(f"Total empty low limits replaced with 0: {len(diffs_zero)}")

# Write to a proposed file instead of overwriting the original yet
df.to_excel('D:/ex_work/gpo_AirQualityReview_Project/data/SetPointLimit_B10_proposed.xlsx', index=False)
