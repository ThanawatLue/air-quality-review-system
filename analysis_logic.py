import pandas as pd
import os
import math
import time
import io
import sys
import traceback
import hashlib
import audit_trail  # GAMP 5: UR-DI-01 Secure Audit Trail

def get_file_hash(file_path):
    """GAMP 5: UR-DI-03 Calculate SHA256 hash of a file for traceability"""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        return f"ERROR: {str(e)}"

def find_header(line_lst): #หา Header ของ CSV จาก BAS เพื่อตั้งเป็น start row สำหรับ read
    for i,v in enumerate(line_lst):
        if '<>Date' in v:
            return i

def find_point_mapping(line_lst, target_room_id, point_type=None): # Find which point column contains data for target room
    """
    Find which Point_X column contains data for the target room based on header mappings.
    Returns the point column name (e.g., 'Point_3') or None if not found.
    Enhanced with better room matching and debugging.
    Now supports all point types: TEMP, HUM, PRES
    """
    # Extract room number from target_room_id (e.g., "1-P040" from "1-P040")
    room_number = target_room_id.split('_')[-1] if '_' in target_room_id else target_room_id
    
    # Create comprehensive matching patterns
    room_id_patterns = [
        room_number,  # Exact room number (e.g., "1-P040")
        room_number.replace('-', ''),  # Without hyphens (e.g., "1P040")
        room_number.split('-')[-1],  # Last part only (e.g., "P040")
        target_room_id,  # Full target ID
        target_room_id.replace('-', ''),  # Full ID without hyphens
    ]
    
    # Determine what type of points to look for
    if point_type:
        point_type = point_type.upper()
        if point_type == "TEMP":
            search_patterns = ['ROOM TEMP', '.RMT']
        elif point_type == "HUM":
            search_patterns = ['ROOM HUM', '.RMH']
        elif point_type == "PRES":
            search_patterns = ['ROOM PRES', '.RPT']
        else:
            search_patterns = [f'ROOM {point_type}']
    else:
        # Auto-detect from file content
        search_patterns = ['ROOM TEMP', 'ROOM HUM', 'ROOM PRES', '.RMT', '.RMH', '.RPT']
    
    # Find all relevant points
    all_points = []
    for line in line_lst:
        if 'Point_' in line and any(pattern in line for pattern in search_patterns):
            parts = line.replace('"','').split(',')
            if len(parts) >= 2:
                point_name = parts[0].strip().replace(':', '')  # Remove trailing colon
                room_identifier = parts[1].strip()
                all_points.append((point_name, room_identifier))
    
    # Try to find exact match first (most reliable)
    for point_name, room_identifier in all_points:
        for pattern in room_id_patterns:
            if pattern in room_identifier and room_identifier == pattern:
                return point_name
    
    # Then try partial matches with better scoring
    best_match = None
    best_score = 0
    
    for point_name, room_identifier in all_points:
        for pattern in room_id_patterns:
            if pattern in room_identifier:
                # Score based on match specificity
                score = len(pattern) / len(room_identifier) if room_identifier else 0
                if pattern == room_identifier:
                    score = 1.0  # Perfect match
                elif pattern == room_number:
                    score = 0.9  # Room number match
                elif pattern == room_number.replace('-', ''):
                    score = 0.8  # Room number without hyphens
                
                if score > best_score:
                    best_score = score
                    best_match = point_name
    
    if best_match:
        return best_match
    
    return None

def find_continuous_ranges(lst, min_length = 2): #หาช่วงเวลาที่ค่ามันต่อกัน
    if len(lst) == 0:
        return []
    result = []
    lst = list(lst)
    start = lst[0]
    current_range = [start]

    for i in range(1, len(lst)):
        if lst[i] == lst[i-1] + 1:
            current_range.append(lst[i])
        else:
            if len(current_range) >= min_length:
                result.append((current_range[0], current_range[-1]))
            start = lst[i]
            current_range = [start]

    if len(current_range) >= min_length:
        result.append((current_range[0], current_range[-1]))

    return result

def get_file_date_range(file_path):
    """GAMP 5: UR-DI-02 Trust internal data for temporal boundaries.
    Peeks at the start and end of the CSV to find the actual date range.
    """
    start_date = None
    end_date = None
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            if not lines: return None, None
            
            # Find Start Date (peek first 150 lines)
            for line in lines[:150]:
                if any(sep in line for sep in ['/', '-']):
                    parts = line.replace('"', '').split(',')
                    for part in parts:
                        part_s = part.strip()
                        if any(sep in part_s for sep in ['/', '-']) and len(part_s) >= 8:
                            try:
                                dt = pd.to_datetime(part_s, errors='coerce', dayfirst=False)
                                if pd.notnull(dt) and 2000 < dt.year < 2100:
                                    if start_date is None: start_date = dt.date()
                                    break
                            except: continue
                if start_date: break
            
            # Find End Date (peek last 150 lines)
            for line in reversed(lines[-150:]):
                if any(sep in line for sep in ['/', '-']):
                    parts = line.replace('"', '').split(',')
                    for part in parts:
                        part_s = part.strip()
                        if any(sep in part_s for sep in ['/', '-']) and len(part_s) >= 8:
                            try:
                                dt = pd.to_datetime(part_s, errors='coerce', dayfirst=False)
                                if pd.notnull(dt) and 2000 < dt.year < 2100:
                                    if end_date is None: end_date = dt.date()
                                    break
                            except: continue
                if end_date: break
                
    except:
        pass
    return start_date, end_date

def prepare_df(file_path, target_room_id=None): # dataframe  analyse
    # Read-Only Data Access: Strict 'r' mode to prevent modification of raw data (FS 2.4)
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        line_lst = [line.replace('"','').replace('\n','') for line in file.readlines()]
        header_index = find_header(line_lst)
        if header_index is None:
            raise ValueError(f"ERR-001: Critical Error - Header '<>Date' not found in file: {file_path}")
        
        # Extract room identifier from filename if target_room_id not provided
        if target_room_id is None:
            filename = os.path.basename(file_path)
            base_name = os.path.splitext(filename)[0]
            parts = base_name.split('_')
            if len(parts) >= 3:
                target_room_id = '_'.join(parts[:-2])
            elif len(parts) >= 1:
                target_room_id = parts[0]
        
        # Find which point column contains pressure data for this room
        pressure_point = find_point_mapping(line_lst, target_room_id) if target_room_id else None
        
        # Parse data
        line_lst = [line.split(',') for line in line_lst]
        df = pd.DataFrame(line_lst[header_index:])
        df.columns = df.iloc[0]
        df = df[1:]
        df = df[~df["<>Date"].str.contains('*', regex=False, na=False)]
        # Flexible parsing: Handle M/D/YYYY, D/M/YYYY or YYYY-MM-DD automatically
        df['DateTime'] = pd.to_datetime(df["<>Date"] + " " + df["Time"], errors='coerce')
        df = df.drop_duplicates(subset=['DateTime'])
        df = df.reset_index(drop=True).dropna()
        
        # Fixed static mapping: Point_1=Temperature, Point_2=Humidity, Point_3=Pressure
        column_mapping = {"Point_1": "Temperature", "Point_2": "Humidity", "Point_3": "Pressure"}
        
        df = df.rename(columns=column_mapping)
        
        # Ensure required columns exist and validate
        required_cols = ['DateTime', 'Temperature', 'Humidity', 'Pressure']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            raise ValueError("ERR-005: Invalid File Format - Required columns not found.")
        
        df = df.reindex(columns=required_cols)
        
        # Convert to numeric with error handling
        numeric_cols = ['Temperature', 'Humidity', 'Pressure']
        for col in numeric_cols:
            if col in df.columns:
                original_nulls = df[col].isna().sum()
                df[col] = pd.to_numeric(df[col], errors='coerce')
                new_nulls = df[col].isna().sum()
                if new_nulls > original_nulls:
                    audit_trail.log_event("WARNING", f"Non-numeric data found in column {col} for file {os.path.basename(file_path)}")
        
        # Validate that we have pressure data
        if 'Pressure' in df.columns and df['Pressure'].isna().all():
            print(f"Warning: No valid pressure data found in {file_path}")
    
    return df

def find_compare_path(file_path_lst, setpoint_df, room_num): #หา pressure corridor เอาไว้เทียบ
    try:
        compare_room = setpoint_df[setpoint_df['Room_number'].astype(str) == room_num]['Room_Pressure_Comparison'].values[0]
        for match_path in file_path_lst:
            if os.path.basename(match_path).split('_')[0] == compare_room:
                return compare_room, match_path
        return room_num, None 
    except (IndexError, KeyError):
        return room_num, None

def check_reverse_violations(corridor_room_num, corridor_df, start_idx, end_idx, setpoint_df, selected_rooms, prepared_dfs_cache):
    summary_lines = []
    dependent_rooms_df = setpoint_df[
        (setpoint_df['Room_number'].astype(str) != corridor_room_num) &
        (setpoint_df['Room_Pressure_Comparison'].astype(str) == corridor_room_num) &
        (setpoint_df['Room_number'].astype(str).isin(selected_rooms))
    ]
    if dependent_rooms_df.empty: return []
    corridor_violation_df = corridor_df.loc[start_idx:end_idx]
    for _, dependent_row in dependent_rooms_df.iterrows():
        dependent_room_num = str(dependent_row['Room_number'])
        low_limit_d = dependent_row.get('Pressure_Low_Limit', None)
        # 45 Pa type rooms (P_low >= 35) should be ABOVE corridor; otherwise 15/30 Pa rooms below corridor
        is_high_pressure_d = (not pd.isna(low_limit_d) and float(low_limit_d) >= 35) if low_limit_d is not None else False
        if dependent_room_num not in prepared_dfs_cache: continue
        df_d = prepared_dfs_cache[dependent_room_num]
        # CRR-TC-02: Temporal Alignment Logic Verification (Ref: CRR-02)
        # Use merge_asof to allow 60s tolerance between different sensor timestamps
        comparison_df = pd.merge_asof(
            corridor_violation_df[['DateTime', 'Pressure']].sort_values('DateTime'),
            df_d[['DateTime', 'Pressure']].sort_values('DateTime'),
            on='DateTime', direction='nearest', tolerance=pd.Timedelta('60s'),
            suffixes=(f'_{corridor_room_num}', f'_{dependent_room_num}')
        ).dropna(subset=[f'Pressure_{dependent_room_num}']).reset_index(drop=True)

        if is_high_pressure_d:
            # Dependent room is 45/60 Pa. It should be ABOVE the corridor.
            # Violation if corridor > room (the corridor is 'over' the high pressure room)
            bool_cond = comparison_df[f'Pressure_{corridor_room_num}'] > comparison_df[f'Pressure_{dependent_room_num}']
            mode = "over" 
        else:
            # Dependent room is 15/30 Pa. It should be BELOW the corridor.
            # Violation if room > corridor (the corridor is 'under' the low pressure room)
            bool_cond = comparison_df[f'Pressure_{dependent_room_num}'] > comparison_df[f'Pressure_{corridor_room_num}']
            mode = "under"

        true_indices = bool_cond[bool_cond].index
        if not true_indices.empty:
            print(f"      REVERSE {mode.upper()} violation data relative to {dependent_room_num}:")
            rev_violation_df = comparison_df.loc[true_indices].copy()
            rev_violation_df['Diff'] = rev_violation_df[f'Pressure_{corridor_room_num}'] - rev_violation_df[f'Pressure_{dependent_room_num}']
            print(rev_violation_df.to_string(index=False))
            print("")

            true_ranges = find_continuous_ranges(true_indices.tolist(), min_length=1)
            for r_start, r_end in true_ranges:
                t_start = comparison_df['DateTime'].iloc[r_start]
                t_end = comparison_df['DateTime'].iloc[r_end]
                # Unified format: mode room_id (e.g., over 1-P036)
                summary_lines.append(f"\n  - {t_start.strftime('%H:%M')} to {t_end.strftime('%H:%M')} {mode} {dependent_room_num}")
    return summary_lines

def get_plot_info(folder_path, setpoint_path, selected_rooms, start_date, end_date, limits):
    try:
        setpoint_df = pd.read_excel(setpoint_path)
        start_dt = pd.to_datetime(start_date).tz_localize(None)
        end_dt = pd.to_datetime(end_date).tz_localize(None)
        all_csv_files = []
        for root, dirs, files in os.walk(folder_path):
            for file_name in files:
                if file_name.lower().endswith(".csv"): all_csv_files.append(os.path.join(root, file_name))
        
        room_data_map = {}
        for f_path in all_csv_files:
            file_name = os.path.basename(f_path)
            # Standard BAS split: [ROOM]_[DATE]_[TIME].csv
            # But M5 files might be M5 2-P173_DATE_TIME.csv
            base_name = os.path.splitext(file_name)[0]
            parts = base_name.split('_')
            if len(parts) < 3: continue
            
            # Reconstruct Room ID by joining all parts except the last two (date and time)
            room_id = '_'.join(parts[:-2])
            
            if room_id not in selected_rooms: continue
            
            try:
                df = prepare_df(f_path, room_id)
                df['DateTime'] = df['DateTime'].dt.tz_localize(None)
                mask = (df['DateTime'] >= start_dt) & (df['DateTime'] <= end_dt)
                if mask.any():
                    if room_id not in room_data_map: room_data_map[room_id] = []
                    room_data_map[room_id].append(df[mask])
            except Exception as e:
                print(f"Error processing file {file_name}: {e}")

        plot_data = {}
        summary = []
        violation_intervals = []

        for room_id in selected_rooms:
            if room_id not in room_data_map or not room_data_map[room_id]: continue
            df = pd.concat(room_data_map[room_id]).sort_values('DateTime').drop_duplicates('DateTime').reset_index(drop=True)
            if df.empty: continue
            
            # --- Get Room-Specific Limits from Excel ---
            row_sp = setpoint_df[setpoint_df['Room_number'].astype(str) == room_id]
            if row_sp.empty: continue
            
            # Business Logic: Analysis MUST use Excel Limits
            EX_T_high = float(row_sp['Temperature_Limit'].iloc[0]) if not pd.isna(row_sp['Temperature_Limit'].iloc[0]) else 100
            EX_H_low  = float(row_sp['Humidity_Low_Limit'].iloc[0]) if not pd.isna(row_sp['Humidity_Low_Limit'].iloc[0]) else 0
            EX_H_high = float(row_sp['Humidity_High_Limit'].iloc[0]) if not pd.isna(row_sp['Humidity_High_Limit'].iloc[0]) else 100
            EX_P_low  = float(row_sp['Pressure_Low_Limit'].iloc[0]) if not pd.isna(row_sp['Pressure_Low_Limit'].iloc[0]) else -999
            EX_P_high = float(row_sp['Pressure_High_Limit'].iloc[0]) if not pd.isna(row_sp['Pressure_High_Limit'].iloc[0]) else 999
            
            room_name_raw = row_sp['Room_name'].iloc[0]
            room_name = str(room_name_raw) if not pd.isna(room_name_raw) else "Unknown Room"
            
            # --- Clean Data for JSON (CRITICAL: Convert to object type first to allow None) ---
            df_clean = df.copy()
            df_clean = df_clean.astype(object).where(pd.notnull(df_clean), None)
            
            plot_data[room_id] = {
                "name": room_name,
                "times": df['DateTime'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist(),
                "temp": df_clean['Temperature'].tolist(), 
                "hum": df_clean['Humidity'].tolist(), 
                "press": df_clean['Pressure'].tolist()
            }

            def get_intervals(series, low, high, times, v_type):
                intervals = []
                # Filter out NaNs for interval calculation logic
                valid_mask = series.notnull()
                s_valid = series[valid_mask]
                t_valid = times[valid_mask]
                
                if high != 0 and high != 999 and high != 100:
                    h_idx = s_valid[s_valid > high].index
                    if not h_idx.empty:
                        raw_ranges = find_continuous_ranges(h_idx.tolist(), min_length=6)
                        for r_start, r_end in raw_ranges:
                            # Re-map indices to original range safely
                            try:
                                t_start, t_end = times.loc[r_start], times.loc[r_end]
                                intervals.append({
                                    "room_id": room_id, "room_name": room_name, "type": v_type,
                                    "start": t_start.strftime('%Y-%m-%d %H:%M:%S'), "end": t_end.strftime('%Y-%m-%d %H:%M:%S'),
                                    "duration": round((t_end - t_start).total_seconds() / 60, 1), "status": "High"
                                })
                            except: continue
                if low != 0 and low != -999:
                    l_idx = s_valid[s_valid < low].index
                    if not l_idx.empty:
                        raw_ranges = find_continuous_ranges(l_idx.tolist(), min_length=6)
                        for r_start, r_end in raw_ranges:
                            try:
                                t_start, t_end = times.loc[r_start], times.loc[r_end]
                                intervals.append({
                                    "room_id": room_id, "room_name": room_name, "type": v_type,
                                    "start": t_start.strftime('%Y-%m-%d %H:%M:%S'), "end": t_end.strftime('%Y-%m-%d %H:%M:%S'),
                                    "duration": round((t_end - t_start).total_seconds() / 60, 1), "status": "Low"
                                })
                            except: continue
                return intervals

            t_intv = get_intervals(df['Temperature'], 0, EX_T_high, df['DateTime'], "Temperature")
            h_intv = get_intervals(df['Humidity'], EX_H_low, EX_H_high, df['DateTime'], "Humidity")
            p_intv = get_intervals(df['Pressure'], EX_P_low, EX_P_high, df['DateTime'], "Pressure")
            
            violation_intervals.extend(t_intv + h_intv + p_intv)
            summary.append({"room_id": room_id, "room_name": room_name, "temp_v": len(t_intv), "hum_v": len(h_intv), "press_v": len(p_intv)})
        
        return {"summary": summary, "plot_data": plot_data, "violation_intervals": violation_intervals}
    except Exception as e:
        traceback.print_exc(); return {"error": str(e)}

def parse_filename_for_datetime(filename, file_path=None):
    """Parses date from filename and ALWAYS subtracts 1 day as per legacy business logic.
    Used mainly for UI speed and as a fallback.
    BAS Format: [ROOM]_[MM-DD-YY]_[HH-MM].csv
    """
    try:
        base_name = os.path.splitext(filename)[0]
        parts = base_name.split('_')
        if len(parts) >= 3:
            # We take the last two parts as DATE and TIME
            date_part = parts[-2] 
            time_part = parts[-1]
            
            # Join with time part and parse as MM-DD-YY
            timestamp_str = f"{date_part}_{time_part}"
            # Using format='%m-%d-%y_%H-%M' strictly for BAS standard
            parsed_dt = pd.to_datetime(timestamp_str, format='%m-%d-%y_%H-%M', errors='coerce')
            
            if pd.notnull(parsed_dt):
                # Business Logic: Data is for the PREVIOUS day
                return (parsed_dt - pd.Timedelta(days=1)).date()
    except Exception:
        pass
    return None

def analyze_files(folder_path, setpoint_path, selected_rooms=None, start_date=None, end_date=None):
    old_stdout = sys.stdout
    sys.stdout = log_stream = io.StringIO()
    try:
        try:
            # Read-Only Access to Configuration File
            setpoint_df = pd.read_excel(setpoint_path)
        except FileNotFoundError:
            raise ValueError("ERR-002: Limit File Not Found")
            
        all_corridor_rooms = set(setpoint_df['Room_Pressure_Comparison'].dropna().astype(str).unique()) if 'Room_Pressure_Comparison' in setpoint_df.columns else set()
        tick_mark, cross_mark = 'Passed', 'Out of spec'
        start_dt = pd.to_datetime(start_date).tz_localize(None) if start_date else None
        end_dt = pd.to_datetime(end_date).tz_localize(None) if end_date else None

        # GAMP 5: UR-DI-01 Log analysis start
        limit_hash = get_file_hash(setpoint_path)
        audit_trail.log_event("ANALYSIS_START", f"Folder: {folder_path} | Limit_Hash: {limit_hash}")

        all_csv_files = []
        for root, dirs, files in os.walk(folder_path):
            for file_name in files:
                if file_name.lower().endswith(".csv"): all_csv_files.append(os.path.join(root, file_name))
        
        relevant_files = []
        for f_path in all_csv_files:
            f_start, f_end = get_file_date_range(f_path)
            
            # Fallback to filename if internal peeking fails
            if not f_start:
                f_dt = parse_filename_for_datetime(os.path.basename(f_path))
                if f_dt: f_start = f_end = f_dt
            
            if f_start and f_end:
                # GAMP 5: UR-FN-25 Range Continuity (Overlapping Range Check)
                # A file is relevant if its range [f_start, f_end] overlaps with [start_dt, end_dt]
                if not (f_end < start_dt.date() or f_start > end_dt.date()):
                    relevant_files.append(f_path)

        if not relevant_files:
            print("No CSV files found matching criteria.")
            audit_trail.log_event("ANALYSIS_FAILED", "No CSV files found matching criteria.")
            return None, log_stream.getvalue()

        # Group by the date of the analysis (using start_dt to end_dt as the business dates)
        # For simplicity and GAMP 5 traceability, we process the full requested range as a single 'run'
        # unless multiple days are requested.
        date_grouped_files = {}
        for d in pd.date_range(start_dt.date(), end_dt.date()):
            d_date = d.date()
            # For each day in the requested range, find files that cover it
            for f_path in relevant_files:
                f_start, f_end = get_file_date_range(f_path)
                if not f_start: # Fallback again
                    f_dt = parse_filename_for_datetime(os.path.basename(f_path))
                    if f_dt: f_start = f_end = f_dt
                
                if f_start and f_end and f_start <= d_date <= f_end:
                    if d_date not in date_grouped_files: date_grouped_files[d_date] = []
                    date_grouped_files[d_date].append(f_path)

        report_data = [] # List to hold report rows, including special date header rows
        
        # Iterate through sorted dates
        for current_date in sorted(date_grouped_files.keys()):
            print(f"\n============================================================")
            print(f" DATE: {current_date.strftime('%Y-%m-%d')}")
            print(f"============================================================\n")
            
            # Add a special header row for the Excel report
            report_data.append({"is_date_header": True, "date_text": f"DATE: {current_date.strftime('%Y-%m-%d')}"})
            
            day_files = date_grouped_files[current_date]
            prepared_dfs_cache = {}
            day_file_paths = []
            
            for f_path in day_files:
                base_name = os.path.splitext(os.path.basename(f_path))[0]
                room_id = '_'.join(base_name.split('_')[:-2])
                if room_id in selected_rooms:
                    day_file_paths.append(f_path)
                    prepared_dfs_cache[room_id] = prepare_df(f_path, room_id)
                    # GAMP 5: UR-DI-03 Traceability: Log each file hash processed
                    f_hash = get_file_hash(f_path)
                    audit_trail.log_event("FILE_PROCESSED", f"Room: {room_id} | File: {os.path.basename(f_path)} | SHA256: {f_hash}")

            for file_path in day_file_paths:
                room_num = '_'.join(os.path.splitext(os.path.basename(file_path))[0].split('_')[:-2])
                print(f"Processing Room: {room_num}")
                setpoint_row = setpoint_df[setpoint_df['Room_number'].astype(str) == room_num]
                if setpoint_row.empty: continue
                              
                # OQ-TC-03: Data Integrity & OQ-TC-23: Logical Constraints
                try:
                    T_lim = float(setpoint_row['Temperature_Limit'].iloc[0]) if not pd.isna(setpoint_row['Temperature_Limit'].iloc[0]) else 100
                except (ValueError, TypeError):
                    raise ValueError("ERR-003: Invalid Configuration - High Limit must be a number")
                
                try:
                    H_low = float(setpoint_row['Humidity_Low_Limit'].iloc[0]) if not pd.isna(setpoint_row['Humidity_Low_Limit'].iloc[0]) else 0
                    H_high = float(setpoint_row['Humidity_High_Limit'].iloc[0]) if not pd.isna(setpoint_row['Humidity_High_Limit'].iloc[0]) else 100
                    P_low = float(setpoint_row['Pressure_Low_Limit'].iloc[0]) if not pd.isna(setpoint_row['Pressure_Low_Limit'].iloc[0]) else None
                    P_high = float(setpoint_row['Pressure_High_Limit'].iloc[0]) if not pd.isna(setpoint_row['Pressure_High_Limit'].iloc[0]) else None
                    
                    if H_high < H_low:
                        raise ValueError("ERR-006: Configuration Error - High Limit cannot be lower than Low Limit or Low Limit cannot be higher than High Limit.")
                    if P_low is not None and P_high is not None and P_high < P_low:
                        raise ValueError("ERR-006: Configuration Error - High Limit cannot be lower than Low Limit or Low Limit cannot be higher than High Limit.")
                except (ValueError, TypeError) as e:
                    if "ERR-006" in str(e): raise e
                    raise ValueError("ERR-003: Invalid Configuration - Limit values must be numeric")
                
                df = prepared_dfs_cache.get(room_num)
                if df is None: continue
                
                # CRR-TC-02: Apply strict row-level temporal filtering
                # Only analyze data within the exact start/end window selected in UI
                df = df[(df['DateTime'] >= start_dt) & (df['DateTime'] <= end_dt)].copy()
                if df.empty: continue
                
                # --- 1. Temperature Check ---
                t_df_all = df[df['Temperature'] > T_lim]
                # Module 3: 10-Minute Gap Threshold / 25-Minute Rule
                # Enforce strict continuity: diff(5) == 1500s ensures 6 points (25 mins) are exactly 5 mins apart.
                # If any gap > 300s exists, diff(5) will not equal 1500, effectively resetting the counter.
                t_25 = t_df_all[t_df_all['DateTime'].diff(5).apply(lambda x: x.total_seconds()) == 1500]
                t_idx = sorted(list(set([j for i in t_25.index for j in range(max(i-5, 0), i+1)])))
                temp_res = f'Temperature: {tick_mark}'
                if t_idx:
                    print(f"Temperature Violations Found for {room_num}:")
                    print(df.loc[t_idx].to_string(index=False))
                    temp_res = [f'Temperature: {cross_mark}']
                    for i in find_continuous_ranges(t_idx):
                        t_range = df.loc[i[0]:i[1]]
                        temp_res.append(f'\n{t_range["DateTime"].dt.strftime("%H:%M").iloc[0]} to {t_range["DateTime"].dt.strftime("%H:%M").iloc[-1]} ({t_range["Temperature"].min()} to {t_range["Temperature"].max()} °C)')
                    temp_res = ''.join(temp_res)
                    print("-------------------------------")

                # --- 1.1 Temperature Data Loss Check ---
                t_loss_idx = df[df['Temperature'].isna()].index.tolist()
                if t_loss_idx:
                    print(f"Temperature Data Loss Found for {room_num}:")
                    print_df = df.loc[t_loss_idx, ['DateTime', 'Temperature']].copy()
                    print_df['Temperature'] = 'Data Loss'
                    print(print_df.to_string(index=False))
                    loss_lines = []
                    for i in find_continuous_ranges(t_loss_idx, min_length=1):
                        t_range = df.loc[i[0]:i[1]]
                        loss_lines.append(f'\n{t_range["DateTime"].dt.strftime("%H:%M").iloc[0]} to {t_range["DateTime"].dt.strftime("%H:%M").iloc[-1]}')
                    
                    if temp_res == f'Temperature: {tick_mark}':
                        temp_res = f'Temperature: Data Loss' + ''.join(loss_lines)
                    else:
                        temp_res = temp_res.replace(f'Temperature: {cross_mark}', f'Temperature: {cross_mark} & Data Loss') + ''.join(loss_lines)

                # --- 2. Humidity Check ---
                h_low_df = df[df['Humidity'] < H_low]
                h_high_df = df[df['Humidity'] > H_high]
                # Module 3: 10-Minute Gap Threshold / 25-Minute Rule (Strict Continuity)
                h_low_idx = h_low_df[h_low_df['DateTime'].diff(5).apply(lambda x: x.total_seconds()) == 1500].index
                h_high_idx = h_high_df[h_high_df['DateTime'].diff(5).apply(lambda x: x.total_seconds()) == 1500].index
                h_low_idx = sorted(list(set([j for i in list(h_low_idx) for j in range(max(i-5, 0), i+1)])))
                h_high_idx = sorted(list(set([j for i in list(h_high_idx) for j in range(max(i-5, 0), i+1)])))
                
                hum_res = f'\nHumidity: {tick_mark}'
                if h_low_idx or h_high_idx:
                    hum_res = [f'\nHumidity: {cross_mark}']
                    
                    if h_high_idx:
                        print(f"Humidity High Violations Found for {room_num}:")
                        print(df.loc[h_high_idx].to_string(index=False))
                        for i in find_continuous_ranges(h_high_idx):
                            h_range = df.loc[i[0]:i[1]]
                            hum_res.append(f'\n{h_range["DateTime"].dt.strftime("%H:%M").iloc[0]} to {h_range["DateTime"].dt.strftime("%H:%M").iloc[-1]} ({h_range["Humidity"].min()} to {h_range["Humidity"].max()} %RH)')
                            
                    if h_low_idx:
                        print(f"Humidity Low Violations Found for {room_num}:")
                        print(df.loc[h_low_idx].to_string(index=False))
                        for i in find_continuous_ranges(h_low_idx):
                            h_range = df.loc[i[0]:i[1]]
                            hum_res.append(f'\n{h_range["DateTime"].dt.strftime("%H:%M").iloc[0]} to {h_range["DateTime"].dt.strftime("%H:%M").iloc[-1]} ({h_range["Humidity"].min()} to {h_range["Humidity"].max()} %RH)')
                    
                    hum_res = ''.join(hum_res)
                    print("-------------------------------")

                # --- 2.1 Humidity Data Loss Check ---
                h_loss_idx = df[df['Humidity'].isna()].index.tolist()
                if h_loss_idx:
                    print(f"Humidity Data Loss Found for {room_num}:")
                    print_df = df.loc[h_loss_idx, ['DateTime', 'Humidity']].copy()
                    print_df['Humidity'] = 'Data Loss'
                    print(print_df.to_string(index=False))
                    loss_lines = []
                    for i in find_continuous_ranges(h_loss_idx, min_length=1):
                        h_range = df.loc[i[0]:i[1]]
                        loss_lines.append(f'\n{h_range["DateTime"].dt.strftime("%H:%M").iloc[0]} to {h_range["DateTime"].dt.strftime("%H:%M").iloc[-1]}')
                    
                    if hum_res == f'\nHumidity: {tick_mark}':
                        hum_res = f'\nHumidity: Data Loss' + ''.join(loss_lines)
                    else:
                        hum_res = hum_res.replace(f'\nHumidity: {cross_mark}', f'\nHumidity: {cross_mark} & Data Loss') + ''.join(loss_lines)

                # --- 3. Pressure Check ---
                if P_low is None or P_high is None:
                    press_res = f'\nPressure: N/A (No specification available)'
                else:
                    # 45 Pa type rooms (P_low >= 35) must stay ABOVE corridor → "over" = Pass, "under" = Out of Spec
                    # 15/30 Pa type rooms (P_low < 35) must stay BELOW corridor → "within" = Pass, "over" = Out of Spec
                    is_high_pressure = (P_low >= 35)

                    p_low_df = df[df['Pressure'] < P_low]
                    p_high_df = df[df['Pressure'] > P_high]
                    # Module 3: 10-Minute Gap Threshold / 25-Minute Rule (Strict Continuity)
                    p_low_idx = p_low_df[p_low_df['DateTime'].diff(5).apply(lambda x: x.total_seconds()) == 1500].index
                    p_high_idx = p_high_df[p_high_df['DateTime'].diff(5).apply(lambda x: x.total_seconds()) == 1500].index

                    p_low_25min_idx = sorted(list(set([j for i in list(p_low_idx) for j in range(max(i-5, 0), i+1)])))
                    p_high_25min_idx = sorted(list(set([j for i in list(p_high_idx) for j in range(max(i-5, 0), i+1)])))

                    press_res = f'\nPressure: {tick_mark}'
                    # Each entry: (start_time, interval_text, is_actual_violation)
                    all_violation_intervals = []

                    math_pressure_room, _ = find_compare_path(day_file_paths, setpoint_df, room_num)
                    math_pressure_df = prepared_dfs_cache.get(math_pressure_room, pd.DataFrame())

                    for viol_idx_list, viol_label, limit_val in [
                        (p_low_25min_idx, "Low", P_low),
                        (p_high_25min_idx, "High", P_high)
                    ]:
                        if not viol_idx_list:
                            continue

                        print(f"{viol_label} Pressure Violations Found for {room_num}:")
                        has_corridor = (room_num != math_pressure_room and not math_pressure_df.empty)

                        for i in find_continuous_ranges(viol_idx_list):
                            p_range = df.loc[i[0]:i[1]]
                            corr_status = ""
                            is_actual_violation = True  # default until corridor comparison says otherwise

                            if has_corridor:
                                # CRR-TC-02: Temporal Alignment Logic Verification (Ref: CRR-02)
                                # Align room and corridor pressure data within a 60s window
                                comp = pd.merge_asof(
                                    p_range[['DateTime', 'Pressure']].sort_values('DateTime'),
                                    math_pressure_df[['DateTime', 'Pressure']].sort_values('DateTime'),
                                    on='DateTime', direction='nearest', tolerance=pd.Timedelta('60s'),
                                    suffixes=(f'_{room_num}', f'_{math_pressure_room}')
                                ).dropna(subset=[f'Pressure_{math_pressure_room}'])
                                comp['Diff'] = comp[f'Pressure_{room_num}'] - comp[f'Pressure_{math_pressure_room}']
                                print(f"  - Interval {p_range['DateTime'].iloc[0]} to {p_range['DateTime'].iloc[-1]} (Corridor: {math_pressure_room})")
                                print(f"    Violation Type: {viol_label} ({'Above' if viol_label == 'High' else 'Below'} {limit_val} Pa)")
                                print(comp.to_string(index=False))

                                if not comp.empty:
                                    room_over_corridor = comp['Diff'].mean() >= 0
                                    if is_high_pressure:
                                        # 45 Pa rooms: over corridor = safe (Pass); under corridor = Out of Spec
                                        if room_over_corridor:
                                            corr_status = f" over {math_pressure_room}"
                                            is_actual_violation = False
                                        else:
                                            corr_status = f" under {math_pressure_room}"
                                            is_actual_violation = True
                                    else:
                                        # 15/30 Pa rooms: within corridor (room < corridor) = safe (Pass); over corridor = Out of Spec
                                        if room_over_corridor:
                                            corr_status = f" over {math_pressure_room}"
                                            is_actual_violation = True
                                        else:
                                            corr_status = f" within {math_pressure_room}"
                                            is_actual_violation = False
                            else:
                                print(f"  - Interval {p_range['DateTime'].iloc[0]} to {p_range['DateTime'].iloc[-1]}")
                                print(f"    Violation Type: {viol_label} ({'Above' if viol_label == 'High' else 'Below'} {limit_val} Pa)")
                                print(p_range[['DateTime', 'Pressure']].to_string(index=False))

                            rev_lines = []
                            if room_num in all_corridor_rooms:
                                rev_lines = check_reverse_violations(room_num, df, i[0], i[1], setpoint_df, selected_rooms, prepared_dfs_cache)

                            interval_text = (
                                f'\n{p_range["DateTime"].dt.strftime("%H:%M").iloc[0]} to '
                                f'{p_range["DateTime"].dt.strftime("%H:%M").iloc[-1]} '
                                f'({p_range["Pressure"].min():.2f} to {p_range["Pressure"].max():.2f} Pa)'
                                f'{corr_status}' + ''.join(rev_lines)
                            )
                            all_violation_intervals.append((p_range['DateTime'].iloc[0], interval_text, is_actual_violation))

                        print("-------------------------------")

                    if all_violation_intervals:
                        all_violation_intervals.sort(key=lambda x: x[0])
                        has_real_violation = any(v[2] for v in all_violation_intervals)
                        press_res = [f'\nPressure: {cross_mark if has_real_violation else tick_mark}']
                        for _, interval_text, _ in all_violation_intervals:
                            press_res.append(interval_text)
                        press_res = ''.join(press_res)

                # --- 3.1 Pressure Data Loss Check ---
                p_loss_idx = df[df['Pressure'].isna()].index.tolist()
                if p_loss_idx:
                    print(f"Pressure Data Loss Found for {room_num}:")
                    print_df = df.loc[p_loss_idx, ['DateTime', 'Pressure']].copy()
                    print_df['Pressure'] = 'Data Loss'
                    print(print_df.to_string(index=False))
                    loss_lines = []
                    for i in find_continuous_ranges(p_loss_idx, min_length=1):
                        p_range = df.loc[i[0]:i[1]]
                        loss_lines.append(f'\n{p_range["DateTime"].dt.strftime("%H:%M").iloc[0]} to {p_range["DateTime"].dt.strftime("%H:%M").iloc[-1]}')
                    
                    if press_res == f'\nPressure: {tick_mark}':
                        press_res = f'\nPressure: Data Loss' + ''.join(loss_lines)
                    elif press_res.startswith(f'\nPressure: {cross_mark}'):
                        press_res = press_res.replace(f'\nPressure: {cross_mark}', f'\nPressure: {cross_mark} & Data Loss') + ''.join(loss_lines)
                    elif press_res == f'\nPressure: N/A (No specification available)':
                        press_res = f'\nPressure: N/A (Data Loss)' + ''.join(loss_lines)

                # Format pressure spec display
                pressure_spec = "N/A" if (P_low is None or P_high is None) else f"{P_low} - {P_high} Pa"
                
                report_data.append({
                    "is_date_header": False,
                    "Room no.": room_num, "Room name": setpoint_row['Room_name'].iloc[0],
                    "Speification": f"Temperature: \u2264 {T_lim}°C\nHumidity: {H_low} - {H_high} %RH\nPressure: {pressure_spec}", 
                    "Analysis results": temp_res + hum_res + press_res
                })
                print(f"Completed Room: {room_num}\n--------------------")

        # --- Excel Export with Date Headers ---
        output_path = os.path.join('reports', f"AQR_Report_{time.strftime('%Y%m%d_%H%M%S')}.xlsx")
        with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
            wb = writer.book
            ws = wb.add_worksheet('Report')
            
            fmt_header = wb.add_format({'font_name': 'Times New Roman', 'bold': True, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'bg_color': '#b0b0b0'})
            fmt_date = wb.add_format({'font_name': 'Times New Roman', 'bold': True, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'bg_color': '#e2e8f0', 'font_size': 12})
            fmt_center = wb.add_format({'font_name': 'Times New Roman', 'border': 1, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True})
            fmt_left = wb.add_format({'font_name': 'Times New Roman', 'border': 1, 'align': 'left', 'valign': 'vcenter', 'text_wrap': True})
            fmt_top = wb.add_format({'font_name': 'Times New Roman', 'bold': True, 'font_size': 11, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'bg_color': '#b0b0b0'})

            if start_dt and end_dt:
                ws.merge_range('A1:C1', f'Period analyzed: {start_dt.strftime("%Y-%m-%d %H:%M")} to {end_dt.strftime("%Y-%m-%d %H:%M")}', fmt_top)
            
            # GAMP 5: UR-FN-08 Hardcode version and generation date (IQ-TC-01)
            ws.write('D1', f'Software Version: v1.1.0\nGenerated: {time.strftime("%Y-%m-%d %H:%M")}', fmt_center)
            
            headers = ["Room no.", "Room name", "Specification", "Analysis results"]
            for col, val in enumerate(headers): ws.write(1, col, val, fmt_header)
            
            ws.set_column('A:A', 12); ws.set_column('B:B', 35); ws.set_column('C:C', 25); ws.set_column('D:D', 45)
            ws.freeze_panes(2, 0)
            
            current_row = 2
            for item in report_data:
                if item["is_date_header"]:
                    ws.merge_range(current_row, 0, current_row, 3, item["date_text"], fmt_date)
                else:
                    ws.write(current_row, 0, item["Room no."], fmt_center)
                    ws.write(current_row, 1, item["Room name"], fmt_left)
                    ws.write(current_row, 2, item["Speification"], fmt_left)
                    ws.write(current_row, 3, item["Analysis results"], fmt_left)
                current_row += 1

        # GAMP 5: UR-DI-01 Log Success and Report Identity
        report_name = os.path.basename(output_path)
        audit_trail.log_event("ANALYSIS_SUCCESS", f"Report: {report_name}")
        
        return output_path, log_stream.getvalue()
    except Exception as e:
        traceback.print_exc(file=log_stream); 
        audit_trail.log_event("ANALYSIS_FAILED", f"Error: {str(e)}")
        return None, log_stream.getvalue()
    finally: sys.stdout = old_stdout
