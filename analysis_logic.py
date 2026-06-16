import pandas as pd
import os
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

def clean_room_num_or_name(val):
    if not val or not isinstance(val, str):
        return val
    # Strip "M5 " prefix if present (e.g. "M5 2-P135" -> "2-P135")
    if val.startswith("M5 "):
        val = val[3:]
    elif "M5 " in val:
        val = val.replace("M5 ", "")
    # Clean 2-P092[082} to 2-P092 [082]
    # Replace curly brace first
    cleaned = val.replace("}", "]")
    if "2-P092[082]" in cleaned:
        cleaned = cleaned.replace("2-P092[082]", "2-P092 [082]")
    elif "2-P092[083]" in cleaned:
        cleaned = cleaned.replace("2-P092[083]", "2-P092 [083]")
    return cleaned

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
                    line_clean = line.replace('"', '')
                    is_semicolon = ';' in line_clean
                    parts = line_clean.split(';') if is_semicolon else line_clean.split(',')
                    for part in parts:
                        part_s = part.strip()
                        if any(sep in part_s for sep in ['/', '-']) and len(part_s) >= 8:
                            try:
                                dt = pd.to_datetime(part_s, errors='coerce', dayfirst=is_semicolon)
                                if pd.notnull(dt) and 2000 < dt.year < 2100:
                                    if start_date is None: start_date = dt.date()
                                    break
                            except: continue
                if start_date: break
            
            # Find End Date (peek last 150 lines)
            for line in reversed(lines[-150:]):
                if any(sep in line for sep in ['/', '-']):
                    line_clean = line.replace('"', '')
                    is_semicolon = ';' in line_clean
                    parts = line_clean.split(';') if is_semicolon else line_clean.split(',')
                    for part in parts:
                        part_s = part.strip()
                        if any(sep in part_s for sep in ['/', '-']) and len(part_s) >= 8:
                            try:
                                dt = pd.to_datetime(part_s, errors='coerce', dayfirst=is_semicolon)
                                if pd.notnull(dt) and 2000 < dt.year < 2100:
                                    if end_date is None: end_date = dt.date()
                                    break
                            except: continue
                if end_date: break
                
    except:
        pass
    return start_date, end_date

def prepare_df(file_path, target_room_id=None, setpoint_df=None): # dataframe  analyse
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
        
        # Parse data
        line_lst = [line.split(',') for line in line_lst]
        df = pd.DataFrame(line_lst[header_index:])
        df.columns = df.iloc[0]
        df = df[1:]
        df = df[~df["<>Date"].str.contains('*', regex=False, na=False)]
        # Flexible parsing: Handle M/D/YYYY, D/M/YYYY or YYYY-MM-DD automatically
        df['DateTime'] = pd.to_datetime(df["<>Date"] + " " + df["Time"], errors='coerce')
        if df['DateTime'].duplicated().any():
            dup_series = df[df['DateTime'].duplicated()]['DateTime'].dropna()
            if not dup_series.empty:
                dup_series_sorted = dup_series.sort_values()
                dup_count = len(dup_series_sorted)
                dup_start = dup_series_sorted.iloc[0].strftime('%Y-%m-%d %H:%M:%S')
                dup_stop = dup_series_sorted.iloc[-1].strftime('%Y-%m-%d %H:%M:%S')
                warn_msg = f"[WARNING] ERR-008: Duplicate Timestamps Detected in file {os.path.basename(file_path)} (Room {target_room_id}). Found {dup_count:,} duplicate timestamps from {dup_start} to {dup_stop}. Dropping duplicates and keeping the first record."
                print(warn_msg)
                audit_trail.log_event("DUPLICATE_TIMESTAMPS_WARN", f"File: {os.path.basename(file_path)} | Room: {target_room_id} | Duplicates: {dup_count} records from {dup_start} to {dup_stop} | Action: Dropped subsequent records (ERR-008)")
        df = df.drop_duplicates(subset=['DateTime'])
        df = df.reset_index(drop=True).dropna()
        
        # Fixed static mapping: Point_1=Temperature, Point_2=Humidity, Point_3=Pressure
        column_mapping = {"Point_1": "Temperature", "Point_2": "Humidity", "Point_3": "Pressure"}
        
        # Check which points are actually present in the dataframe
        available_cols = df.columns.tolist()
        rename_map = {k: v for k, v in column_mapping.items() if k in available_cols}
        df = df.rename(columns=rename_map)
        
        # GxP: Ensure required columns exist based on configuration
        mandatory_cols = ['DateTime']
        if setpoint_df is not None and target_room_id is not None:
            row_sp = setpoint_df[setpoint_df['Room_number'].astype(str) == target_room_id]
            if not row_sp.empty:
                if not pd.isna(row_sp['Temperature_Limit'].iloc[0]):
                    mandatory_cols.append('Temperature')
                humidity_has_spec = (not pd.isna(row_sp['Humidity_Low_Limit'].iloc[0])) and (not pd.isna(row_sp['Humidity_High_Limit'].iloc[0]))
                if humidity_has_spec:
                    mandatory_cols.append('Humidity')
                pressure_has_spec = (not pd.isna(row_sp['Pressure_Low_Limit'].iloc[0])) and (not pd.isna(row_sp['Pressure_High_Limit'].iloc[0]))
                if pressure_has_spec:
                    mandatory_cols.append('Pressure')
        else:
            mandatory_cols = ['DateTime', 'Temperature', 'Humidity']
            
        missing_mandatory = [col for col in mandatory_cols if col not in df.columns]
        
        if missing_mandatory:
            raise ValueError(f"ERR-005: Invalid File Format - Required columns {missing_mandatory} not found. ({os.path.basename(file_path)})")
            
        # Ensure Pressure exists (fill with NaN if missing)
        if 'Pressure' not in df.columns:
            df['Pressure'] = pd.NA
        
        required_cols = ['DateTime', 'Temperature', 'Humidity', 'Pressure']
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
        
    
    return df

def find_compare_path(file_path_lst, setpoint_df, room_num): #หา pressure corridor เอาไว้เทียบ
    try:
        compare_room = setpoint_df[setpoint_df['Room_number'].astype(str) == room_num]['Room_Pressure_Comparison'].values[0]
        setpoint_rooms = set(setpoint_df['Room_number'].astype(str).tolist())
        sorted_setpoint_rooms = sorted(list(setpoint_rooms), key=len, reverse=True)
        for match_path in file_path_lst:
            base = os.path.splitext(os.path.basename(match_path))[0]
            room_id_from_file = None
            for r in sorted_setpoint_rooms:
                if base.startswith(r):
                    room_id_from_file = r
                    break
            if not room_id_from_file:
                room_id_from_file = '_'.join(base.split('_')[:-2])
            if room_id_from_file == compare_room:
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
            print(f"      REVERSE {mode.upper()} violation data relative to {clean_room_num_or_name(dependent_room_num)}:")
            rev_violation_df = comparison_df.loc[true_indices].copy()
            rev_violation_df['Diff'] = rev_violation_df[f'Pressure_{corridor_room_num}'] - rev_violation_df[f'Pressure_{dependent_room_num}']
            print(rev_violation_df.to_string(index=False))
            print("")

            true_ranges = find_continuous_ranges(true_indices.tolist(), min_length=1)
            for r_start, r_end in true_ranges:
                t_start = comparison_df['DateTime'].iloc[r_start]
                t_end = comparison_df['DateTime'].iloc[r_end]
                # Unified format: mode room_id (e.g., over 1-P036)
                summary_lines.append(f"\n  - {t_start.strftime('%H:%M')} to {t_end.strftime('%H:%M')} {mode} {clean_room_num_or_name(dependent_room_num)}")
    return summary_lines

class QueueWriter:
    """Captures print() output, streams lines into a queue, and buffers full log for return value."""
    def __init__(self, log_queue=None):
        self._queue = log_queue
        self._buf = ''
        self._full = io.StringIO()

    def write(self, text):
        self._full.write(text)
        if self._queue is not None:
            self._buf += text
            while '\n' in self._buf:
                line, self._buf = self._buf.split('\n', 1)
                self._queue.put(line)
        return len(text)

    def flush(self):
        pass

    def getvalue(self):
        return self._full.getvalue()

    @property
    def encoding(self):
        return 'utf-8'


def _print_df(df):
    print(df.to_string(index=False))


def _compute_plot_result(room_data_map, setpoint_df, selected_rooms, start_dt, end_dt):
    """Build chart data from pre-loaded DataFrames — shared by analyze_files and get_plot_info."""
    plot_data = {}
    summary = []
    violation_intervals = []

    def get_intervals(series, low, high, times, room_id, room_name, v_type):
        intervals = []
        s_valid = series[series.notnull()]
        if high != 0 and high != 999 and high != 100:
            for r_start, r_end in find_continuous_ranges(s_valid[s_valid > high].index.tolist(), min_length=6):
                try:
                    t_s, t_e = times.loc[r_start], times.loc[r_end]
                    intervals.append({"room_id": room_id, "room_name": room_name, "type": v_type,
                        "start": t_s.strftime('%Y-%m-%d %H:%M:%S'), "end": t_e.strftime('%Y-%m-%d %H:%M:%S'),
                        "duration": round((t_e - t_s).total_seconds() / 60, 1), "status": "High"})
                except: continue
        if low != 0 and low != -999:
            for r_start, r_end in find_continuous_ranges(s_valid[s_valid < low].index.tolist(), min_length=6):
                try:
                    t_s, t_e = times.loc[r_start], times.loc[r_end]
                    intervals.append({"room_id": room_id, "room_name": room_name, "type": v_type,
                        "start": t_s.strftime('%Y-%m-%d %H:%M:%S'), "end": t_e.strftime('%Y-%m-%d %H:%M:%S'),
                        "duration": round((t_e - t_s).total_seconds() / 60, 1), "status": "Low"})
                except: continue
        return intervals

    for room_id in selected_rooms:
        if room_id not in room_data_map or not room_data_map[room_id]: continue
        df = pd.concat(room_data_map[room_id]).sort_values('DateTime').drop_duplicates('DateTime').reset_index(drop=True)
        df = df[(df['DateTime'] >= start_dt) & (df['DateTime'] <= end_dt)].reset_index(drop=True)
        if df.empty: continue

        row_sp = setpoint_df[setpoint_df['Room_number'].astype(str) == room_id]
        if row_sp.empty: continue

        EX_T_high = float(row_sp['Temperature_Limit'].iloc[0]) if not pd.isna(row_sp['Temperature_Limit'].iloc[0]) else 100
        EX_H_low  = float(row_sp['Humidity_Low_Limit'].iloc[0]) if not pd.isna(row_sp['Humidity_Low_Limit'].iloc[0]) else 0
        EX_H_high = float(row_sp['Humidity_High_Limit'].iloc[0]) if not pd.isna(row_sp['Humidity_High_Limit'].iloc[0]) else 100
        pressure_has_spec = (not pd.isna(row_sp['Pressure_Low_Limit'].iloc[0])) and (not pd.isna(row_sp['Pressure_High_Limit'].iloc[0]))
        EX_P_low  = float(row_sp['Pressure_Low_Limit'].iloc[0]) if pressure_has_spec else -999
        EX_P_high = float(row_sp['Pressure_High_Limit'].iloc[0]) if pressure_has_spec else 999
        room_name = str(row_sp['Room_name'].iloc[0]) if not pd.isna(row_sp['Room_name'].iloc[0]) else "Unknown Room"

        df_clean = df.copy().astype(object).where(pd.notnull(df), None)
        plot_data[room_id] = {
            "name": room_name,
            "times": df['DateTime'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist(),
            "temp": df_clean['Temperature'].tolist(),
            "hum": df_clean['Humidity'].tolist(),
            "press": df_clean['Pressure'].tolist() if pressure_has_spec else []
        }

        t_intv = get_intervals(df['Temperature'], 0, EX_T_high, df['DateTime'], room_id, room_name, "Temperature")
        h_intv = get_intervals(df['Humidity'], EX_H_low, EX_H_high, df['DateTime'], room_id, room_name, "Humidity")
        p_intv = get_intervals(df['Pressure'], EX_P_low, EX_P_high, df['DateTime'], room_id, room_name, "Pressure") if pressure_has_spec else []
        violation_intervals.extend(t_intv + h_intv + p_intv)
        summary.append({"room_id": room_id, "room_name": room_name, "temp_v": len(t_intv), "hum_v": len(h_intv), "press_v": len(p_intv)})

    return {"summary": summary, "plot_data": plot_data, "violation_intervals": violation_intervals}


def get_plot_info(folder_path, setpoint_path, selected_rooms, start_date, end_date, limits):
    try:
        setpoint_df = pd.read_excel(setpoint_path)
        required_cols = ['Room_number', 'Temperature_Limit', 'Humidity_Low_Limit', 'Humidity_High_Limit', 'Pressure_Low_Limit', 'Pressure_High_Limit']
        missing_cols = [col for col in required_cols if col not in setpoint_df.columns]
        if missing_cols:
            raise ValueError(f"ERR-009: Invalid Limit File Format - Missing required columns: {', '.join(missing_cols)}")
        start_dt = pd.to_datetime(start_date).tz_localize(None)
        end_dt = pd.to_datetime(end_date).tz_localize(None)
        room_data_map = {}
        for root, dirs, files in os.walk(folder_path):
            for file_name in files:
                if not file_name.lower().endswith(".csv"): continue
                f_path = os.path.join(root, file_name)
                parts = os.path.splitext(file_name)[0].split('_')
                if len(parts) < 3: continue
                room_id = '_'.join(parts[:-2])
                if room_id not in selected_rooms: continue
                try:
                    room_data_map.setdefault(room_id, []).append(prepare_df(f_path, room_id, setpoint_df))
                except Exception as e:
                    audit_trail.log_event("PLOT_DATA_ERROR", f"Room: {room_id} | File: {file_name} | Error: {str(e)}")
        return _compute_plot_result(room_data_map, setpoint_df, selected_rooms, start_dt, end_dt)
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


def build_daily_wide_rows(report_data):
    """Transform per-day stacked rows into a wide table keyed by room."""
    day_columns = []
    room_rows = {}
    current_day = None

    for item in report_data:
        if item.get("is_date_header"):
            current_day = item.get("day_column_label") or item.get("date_text", "").replace("DATE: ", "").strip()
            if current_day and current_day not in day_columns:
                day_columns.append(current_day)
            continue

        if not current_day:
            continue

        room_no = str(item.get("Room no.", "")).strip()
        if not room_no:
            continue

        if room_no not in room_rows:
            room_rows[room_no] = {
                "Room no.": item.get("Room no.", ""),
                "Room name": item.get("Room name", ""),
                "Specification": item.get("Specification", ""),
                "days": {}
            }

        if not room_rows[room_no].get("Room name"):
            room_rows[room_no]["Room name"] = item.get("Room name", "")
        if not room_rows[room_no].get("Specification") or room_rows[room_no]["Specification"] == "N/A":
            room_rows[room_no]["Specification"] = item.get("Specification", room_rows[room_no]["Specification"])

        new_result = str(item.get("Analysis results", ""))
        existing_result = room_rows[room_no]["days"].get(current_day)
        if existing_result:
            room_rows[room_no]["days"][current_day] = f"{existing_result}\n---\n{new_result}"
        else:
            room_rows[room_no]["days"][current_day] = new_result

    return day_columns, room_rows

def _analyze_single_room_core(
    df, 
    room_num, 
    setpoint_row, 
    tick_mark, 
    cross_mark, 
    all_corridor_rooms, 
    prepared_dfs_cache, 
    selected_rooms, 
    setpoint_df,
    day_analysis_start,
    day_analysis_end
):
    """
    Standardized, GxP-compliant core analysis for a single room's data.
    Shared identically by Phase I (BAS) and Phase II (EMS).
    """
    # OQ-TC-03: Data Integrity & OQ-TC-23: Logical Constraints
    try:
        T_lim = float(setpoint_row['Temperature_Limit'].iloc[0]) if not pd.isna(setpoint_row['Temperature_Limit'].iloc[0]) else 100
    except (ValueError, TypeError):
        raise ValueError("ERR-003: Invalid Configuration - High Limit must be a number")
    
    try:
        humidity_has_spec = (not pd.isna(setpoint_row['Humidity_Low_Limit'].iloc[0])) and (not pd.isna(setpoint_row['Humidity_High_Limit'].iloc[0]))
        H_low  = float(setpoint_row['Humidity_Low_Limit'].iloc[0])  if humidity_has_spec else 0
        H_high = float(setpoint_row['Humidity_High_Limit'].iloc[0]) if humidity_has_spec else 100
        
        P_low  = float(setpoint_row['Pressure_Low_Limit'].iloc[0])  if not pd.isna(setpoint_row['Pressure_Low_Limit'].iloc[0])  else None
        P_high = float(setpoint_row['Pressure_High_Limit'].iloc[0]) if not pd.isna(setpoint_row['Pressure_High_Limit'].iloc[0]) else None
        
        if humidity_has_spec and H_high < H_low:
            raise ValueError("ERR-006: Configuration Error - High Limit cannot be lower than Low Limit.")
        if P_low is not None and P_high is not None and P_high < P_low:
            raise ValueError("ERR-006: Configuration Error - Pressure High Limit cannot be lower than Low Limit.")
    except (ValueError, TypeError) as e:
        if "ERR-006" in str(e): raise e
        raise ValueError("ERR-003: Invalid Configuration - Limit values must be numeric")
    
    # Apply strict temporal filtering for the day
    df = df[(df['DateTime'] >= day_analysis_start) & (df['DateTime'] <= day_analysis_end)].copy()
    if df.empty:
        return None

    # --- 1. Temperature Check ---
    t_df_all = df[df['Temperature'] > T_lim]
    # Module 3: 10-Minute Gap Threshold / 25-Minute Rule
    t_25 = t_df_all[t_df_all['DateTime'].diff(5).dt.total_seconds() == 1500]
    t_idx = sorted(list(set([j for i in t_25.index for j in range(max(i-5, 0), i+1)])))
    temp_res = f'Temperature: {tick_mark}'
    if t_idx:
        print(f"Temperature Violations Found for {room_num}: (Limit: ≤ {T_lim} °C)")
        _print_df(df.loc[t_idx][['DateTime', 'Temperature']])
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
        _print_df(print_df)
        loss_lines = []
        for i in find_continuous_ranges(t_loss_idx, min_length=1):
            t_range = df.loc[i[0]:i[1]]
            loss_lines.append(f'\n{t_range["DateTime"].dt.strftime("%H:%M").iloc[0]} to {t_range["DateTime"].dt.strftime("%H:%M").iloc[-1]}')
        
        if temp_res == f'Temperature: {tick_mark}':
            temp_res = f'Temperature: Data Loss' + ''.join(loss_lines)
        else:
            temp_res = temp_res.replace(f'Temperature: {cross_mark}', f'Temperature: {cross_mark} & Data Loss') + ''.join(loss_lines)
        print("-------------------------------")

    # --- 2. Humidity Check ---
    if not humidity_has_spec:
        hum_res = f'\nHumidity: N/A'
    else:
        h_low_df = df[df['Humidity'] < H_low]
        h_high_df = df[df['Humidity'] > H_high]
        
        h_low_idx = h_low_df[h_low_df['DateTime'].diff(5).dt.total_seconds() == 1500].index
        h_high_idx = h_high_df[h_high_df['DateTime'].diff(5).dt.total_seconds() == 1500].index
        
        h_low_idx = sorted(list(set([j for i in list(h_low_idx) for j in range(max(i-5, 0), i+1)])))
        h_high_idx = sorted(list(set([j for i in list(h_high_idx) for j in range(max(i-5, 0), i+1)])))
        
        hum_res = f'\nHumidity: {tick_mark}'
        if h_low_idx or h_high_idx:
            hum_res = [f'\nHumidity: {cross_mark}']
            if h_high_idx:
                print(f"Humidity High Violations Found for {room_num}: (Limit: > {H_high} %RH)")
                _print_df(df.loc[h_high_idx][['DateTime', 'Humidity']])
                for i in find_continuous_ranges(h_high_idx):
                    h_range = df.loc[i[0]:i[1]]
                    hum_res.append(f'\n{h_range["DateTime"].dt.strftime("%H:%M").iloc[0]} to {h_range["DateTime"].dt.strftime("%H:%M").iloc[-1]} ({h_range["Humidity"].min()} to {h_range["Humidity"].max()} %RH)')
                    
            if h_low_idx:
                print(f"Humidity Low Violations Found for {room_num}: (Limit: < {H_low} %RH)")
                _print_df(df.loc[h_low_idx][['DateTime', 'Humidity']])
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
            _print_df(print_df)
            loss_lines = []
            for i in find_continuous_ranges(h_loss_idx, min_length=1):
                h_range = df.loc[i[0]:i[1]]
                loss_lines.append(f'\n{h_range["DateTime"].dt.strftime("%H:%M").iloc[0]} to {h_range["DateTime"].dt.strftime("%H:%M").iloc[-1]}')
            
            if hum_res == f'\nHumidity: {tick_mark}':
                hum_res = f'\nHumidity: Data Loss' + ''.join(loss_lines)
            else:
                hum_res = hum_res.replace(f'\nHumidity: {cross_mark}', f'\nHumidity: {cross_mark} & Data Loss') + ''.join(loss_lines)
            print("-------------------------------")

    # --- 3. Pressure Check ---
    if P_low is None or P_high is None:
        press_res = f'\nPressure: N/A'
    else:
        is_high_pressure = (P_low >= 35)
        p_low_df = df[df['Pressure'] < P_low]
        p_high_df = df[df['Pressure'] > P_high]
        
        p_low_idx = p_low_df[p_low_df['DateTime'].diff(5).dt.total_seconds() == 1500].index
        p_high_idx = p_high_df[p_high_df['DateTime'].diff(5).dt.total_seconds() == 1500].index

        p_low_25min_idx = sorted(list(set([j for i in list(p_low_idx) for j in range(max(i-5, 0), i+1)])))
        p_high_25min_idx = sorted(list(set([j for i in list(p_high_idx) for j in range(max(i-5, 0), i+1)])))

        press_res = f'\nPressure: {tick_mark}'
        all_violation_intervals = []

        # Find compare corridor room directly from setpoint_df
        try:
            compare_room_val = setpoint_df[setpoint_df['Room_number'].astype(str) == room_num]['Room_Pressure_Comparison'].values[0]
            math_pressure_room = str(compare_room_val) if not pd.isna(compare_room_val) else room_num
        except (IndexError, KeyError):
            math_pressure_room = room_num
        math_pressure_df = prepared_dfs_cache.get(math_pressure_room, pd.DataFrame())

        for viol_idx_list, viol_label, limit_val in [
            (p_low_25min_idx, "Low", P_low),
            (p_high_25min_idx, "High", P_high)
        ]:
            if not viol_idx_list:
                continue

            print(f"{viol_label} Pressure Violations Found for {room_num}: (Limit: {P_low} - {P_high} Pa)")
            has_corridor = (room_num != math_pressure_room and not math_pressure_df.empty)

            for i in find_continuous_ranges(viol_idx_list):
                p_range = df.loc[i[0]:i[1]]
                corr_status = ""
                is_actual_violation = True

                if has_corridor:
                    comp = pd.merge_asof(
                        p_range[['DateTime', 'Pressure']].sort_values('DateTime'),
                        math_pressure_df[['DateTime', 'Pressure']].sort_values('DateTime'),
                        on='DateTime', direction='nearest', tolerance=pd.Timedelta('60s'),
                        suffixes=(f'_{room_num}', f'_{math_pressure_room}')
                    ).dropna(subset=[f'Pressure_{math_pressure_room}'])
                    comp['Diff'] = comp[f'Pressure_{room_num}'] - comp[f'Pressure_{math_pressure_room}']
                    
                    print(f"  - Interval {p_range['DateTime'].iloc[0]} to {p_range['DateTime'].iloc[-1]} (Corridor: {clean_room_num_or_name(math_pressure_room)})")
                    print(f"    Violation Type: {viol_label} ({'Above' if viol_label == 'High' else 'Below'} {limit_val} Pa)")
                    _print_df(comp)

                    if not comp.empty:
                        if is_high_pressure:
                            # For high-pressure room (e.g. 40-50 Pa), any point under corridor (< 0) is a GxP violation
                            has_under = (comp['Diff'] < 0).any()
                            if has_under:
                                corr_status = f" under {clean_room_num_or_name(math_pressure_room)}"
                                is_actual_violation = True
                            else:
                                corr_status = f" over {clean_room_num_or_name(math_pressure_room)}"
                                is_actual_violation = False
                        else:
                            # For low-pressure room, any point over corridor (> 0) is a GxP violation
                            has_over = (comp['Diff'] > 0).any()
                            if has_over:
                                corr_status = f" over {clean_room_num_or_name(math_pressure_room)}"
                                is_actual_violation = True
                            else:
                                corr_status = f" within {clean_room_num_or_name(math_pressure_room)}"
                                is_actual_violation = False
                else:
                    print(f"  - Interval {p_range['DateTime'].iloc[0]} to {p_range['DateTime'].iloc[-1]}")
                    print(f"    Violation Type: {viol_label} ({'Above' if viol_label == 'High' else 'Below'} {limit_val} Pa)")
                    _print_df(p_range[['DateTime', 'Pressure']])

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

        # Pressure data loss check
        p_loss_idx = df[df['Pressure'].isna()].index.tolist()
        if p_loss_idx:
            print(f"Pressure Data Loss Found for {room_num}:")
            print_df = df.loc[p_loss_idx, ['DateTime', 'Pressure']].copy()
            print_df['Pressure'] = 'Data Loss'
            _print_df(print_df)
            loss_lines = []
            for i in find_continuous_ranges(p_loss_idx, min_length=1):
                p_range = df.loc[i[0]:i[1]]
                loss_lines.append(f'\n{p_range["DateTime"].dt.strftime("%H:%M").iloc[0]} to {p_range["DateTime"].dt.strftime("%H:%M").iloc[-1]}')
            
            if press_res == f'\nPressure: {tick_mark}':
                press_res = f'\nPressure: Data Loss' + ''.join(loss_lines)
            elif press_res.startswith(f'\nPressure: {cross_mark}'):
                press_res = press_res.replace(f'\nPressure: {cross_mark}', f'\nPressure: {cross_mark} & Data Loss') + ''.join(loss_lines)
            print("-------------------------------")

    # Format specs and append to report
    humidity_spec = "N/A" if not humidity_has_spec else f"{H_low} - {H_high} %RH"
    pressure_spec = "N/A" if (P_low is None or P_high is None) else f"{P_low} - {P_high} Pa"
    
    spec_txt = f"Temperature: \u2264 {T_lim}°C\nHumidity: {humidity_spec}\nPressure: {pressure_spec}"
    analysis_res_txt = temp_res + hum_res + press_res
    
    return spec_txt, analysis_res_txt

def analyze_files(folder_path, setpoint_path, selected_rooms=None, start_date=None, end_date=None, log_queue=None):
    old_stdout = sys.stdout
    sys.stdout = log_stream = QueueWriter(log_queue)
    try:
        try:
            # Read-Only Access to Configuration File
            setpoint_df = pd.read_excel(setpoint_path)
        except FileNotFoundError:
            raise ValueError("ERR-002: Limit File Not Found")
            
        required_cols = ['Room_number', 'Temperature_Limit', 'Humidity_Low_Limit', 'Humidity_High_Limit', 'Pressure_Low_Limit', 'Pressure_High_Limit']
        missing_cols = [col for col in required_cols if col not in setpoint_df.columns]
        if missing_cols:
            raise ValueError(f"ERR-009: Invalid Limit File Format - Missing required columns: {', '.join(missing_cols)}")
            
        all_corridor_rooms = set(setpoint_df['Room_Pressure_Comparison'].dropna().astype(str).unique()) if 'Room_Pressure_Comparison' in setpoint_df.columns else set()
        needed_rooms = set(selected_rooms) if selected_rooms else set()
        if selected_rooms:
            for r in selected_rooms:
                sp_row = setpoint_df[setpoint_df['Room_number'].astype(str) == r]
                if not sp_row.empty and 'Room_Pressure_Comparison' in setpoint_df.columns:
                    comp_val = sp_row['Room_Pressure_Comparison'].iloc[0]
                    if not pd.isna(comp_val):
                        needed_rooms.add(str(comp_val))
                        
        tick_mark, cross_mark = 'Passed', 'Out of spec'
        start_dt = pd.to_datetime(start_date).tz_localize(None) if start_date else None
        end_dt = pd.to_datetime(end_date).tz_localize(None) if end_date else None

        # GAMP 5: UR-DI-01 Log analysis start
        limit_hash = get_file_hash(setpoint_path)
        audit_trail.log_event("ANALYSIS_START", f"Folder: {folder_path} | Limit_Hash: {limit_hash}")

        room_errors = {}

        all_csv_files = []
        for root, dirs, files in os.walk(folder_path):
            for file_name in files:
                if file_name.lower().endswith(".csv"): all_csv_files.append(os.path.join(root, file_name))
        
        # Build date cache once — avoid reading every file twice
        file_date_cache = {}
        for f_path in all_csv_files:
            f_start, f_end = get_file_date_range(f_path)
            if not f_start:
                f_dt = parse_filename_for_datetime(os.path.basename(f_path))
                if f_dt: f_start = f_end = f_dt
            file_date_cache[f_path] = (f_start, f_end)

        relevant_files = [
            f for f, (fs, fe) in file_date_cache.items()
            if fs and fe and not (fe < start_dt.date() or fs > end_dt.date())
        ]

        # GxP Upfront Validation: Verify all selected rooms have valid, complete files (ERR-005)
        sorted_selected = sorted(list(needed_rooms), key=len, reverse=True)
        for room_id in (selected_rooms or []):
            if setpoint_df[setpoint_df['Room_number'].astype(str) == room_id].empty:
                continue
            
            # Check if any CSV file in the input folder matches this room ID
            room_files = []
            for f_path in all_csv_files:
                base_name = os.path.splitext(os.path.basename(f_path))[0]
                matched_r = None
                for r in sorted_selected:
                    if base_name.startswith(r):
                        matched_r = r
                        break
                if not matched_r:
                    matched_r = '_'.join(base_name.split('_')[:-2])
                if matched_r == room_id:
                    room_files.append(f_path)
            
            if not room_files:
                raise ValueError(f"ERR-005: Raw data file not found in {folder_path} for Room {room_id}")
            
            # Check if any file is within the selected date range
            room_files_in_range = [
                f for f in room_files
                if f in file_date_cache and file_date_cache[f][0] and file_date_cache[f][1] and
                not (file_date_cache[f][1] < start_dt.date() or file_date_cache[f][0] > end_dt.date())
            ]
            if not room_files_in_range:
                raise ValueError(f"ERR-005: Raw data for Room {room_id} is missing or out of the selected date range.")
            
            # Validate column completeness
            for f_path in room_files_in_range:
                prepare_df(f_path, room_id, setpoint_df)

        if not relevant_files:
            audit_trail.log_event("ANALYSIS_FAILED", "ERR-010: No Matching Files Found matching criteria.")
            raise ValueError("ERR-010: No Matching Files Found matching criteria.")


        date_grouped_files = {}
        for d in pd.date_range(start_dt.date(), end_dt.date()):
            d_date = d.date()
            for f_path in relevant_files:
                f_start, f_end = file_date_cache[f_path]  # reuse cache — no extra file read
                if f_start and f_end and f_start <= d_date <= f_end:
                    if d_date not in date_grouped_files: date_grouped_files[d_date] = []
                    date_grouped_files[d_date].append(f_path)

        report_data = []
        all_room_dfs = {}  # accumulate dfs across all days for chart — avoids re-reading files

        for current_date in sorted(date_grouped_files.keys()):
            day_start = pd.Timestamp(current_date).tz_localize(None)
            day_end = day_start + pd.Timedelta(hours=23, minutes=55)
            day_analysis_start = max(day_start, start_dt)
            day_analysis_end = min(day_end, end_dt)
            print(f"\n============================================================")
            print(f" DATE: {current_date.strftime('%Y-%m-%d')}")
            print(f"============================================================\n")
            
            # Add a special header row for the Excel report (will update with actual data time span)
            day_header_row = {
                "is_date_header": True,
                "date_text": f"DATE: {current_date.strftime('%Y-%m-%d')}",
                "day_column_label": f"{current_date.strftime('%Y-%m-%d')} ({day_analysis_start.strftime('%H:%M')}-{day_analysis_end.strftime('%H:%M')})"
            }
            report_data.append(day_header_row)
            
            day_files = date_grouped_files[current_date]
            prepared_dfs_cache = {}
            day_file_paths = []
            day_file_to_room = {}
            
            sorted_selected = sorted(list(needed_rooms), key=len, reverse=True)
            for f_path in day_files:
                base_name = os.path.splitext(os.path.basename(f_path))[0]
                room_id = None
                for r in sorted_selected:
                    if base_name.startswith(r):
                        room_id = r
                        break
                if not room_id:
                    room_id = '_'.join(base_name.split('_')[:-2])
                if room_id in needed_rooms:
                    if setpoint_df[setpoint_df['Room_number'].astype(str) == room_id].empty:
                        continue  # No specification defined — intentionally skip, no error
                    try:
                        prepared_df = prepare_df(f_path, room_id, setpoint_df)
                        prepared_df = prepared_df[(prepared_df['DateTime'] >= day_start) & (prepared_df['DateTime'] <= day_end)].copy()
                        if prepared_df.empty:
                            continue
                        if room_id in selected_rooms:
                            day_file_paths.append(f_path)
                            day_file_to_room[f_path] = room_id
                        prepared_dfs_cache[room_id] = prepared_df
                        all_room_dfs.setdefault(room_id, []).append(prepared_df)
                        f_hash = get_file_hash(f_path)
                        audit_trail.log_event("FILE_PROCESSED", f"Room: {room_id} | File: {os.path.basename(f_path)} | SHA256: {f_hash}")
                    except Exception as e:
                        error_msg = f"FILE ERROR [{room_id}]: {os.path.basename(f_path)} — {str(e)}"
                        print(error_msg)
                        traceback.print_exc(file=sys.stdout)
                        audit_trail.log_event("FILE_ERROR", f"Room: {room_id} | File: {os.path.basename(f_path)} | Error: {str(e)}")
                        if "FAILED_ROOMS" not in prepared_dfs_cache: prepared_dfs_cache["FAILED_ROOMS"] = {}
                        prepared_dfs_cache["FAILED_ROOMS"][room_id] = str(e)
                        if room_id in selected_rooms:
                            day_file_paths.append(f_path)
                            day_file_to_room[f_path] = room_id
 
            # Prefer actual data time span from day dataframes; fallback to analysis window.
            day_dfs = [v for k, v in prepared_dfs_cache.items() if k != "FAILED_ROOMS" and isinstance(v, pd.DataFrame) and not v.empty]
            if day_dfs:
                actual_day_start = min(df['DateTime'].min() for df in day_dfs)
                actual_day_end = max(df['DateTime'].max() for df in day_dfs)
                day_header_row["day_column_label"] = f"{current_date.strftime('%Y-%m-%d')} ({actual_day_start.strftime('%H:%M')}-{actual_day_end.strftime('%H:%M')})"
 
            _total_day = len(day_file_paths)
            for _day_idx, file_path in enumerate(day_file_paths, 1):
                try:
                    room_num = day_file_to_room.get(file_path)
                    if not room_num:
                        room_num = '_'.join(os.path.splitext(os.path.basename(file_path))[0].split('_')[:-2])
                    print(f"[{_day_idx}/{_total_day}] Processing Room: {room_num}")
                    
                    # Check if this room failed during prepare_df
                    if "FAILED_ROOMS" in prepared_dfs_cache and room_num in prepared_dfs_cache["FAILED_ROOMS"]:
                        err_reason = prepared_dfs_cache["FAILED_ROOMS"][room_num]
                        sp_row_err = setpoint_df[setpoint_df['Room_number'].astype(str) == room_num]
                        room_name_err = str(sp_row_err['Room_name'].iloc[0]) if not sp_row_err.empty and not pd.isna(sp_row_err['Room_name'].iloc[0]) else "N/A"
                        print(f"[ERROR] Skipping Room {room_num} ({room_name_err}): {err_reason}")
                        audit_trail.log_event("ROOM_SKIPPED_ERROR", f"Room: {room_num} | Name: {room_name_err} | Reason: {err_reason}")
                        room_errors[room_num] = err_reason
                        report_data.append({
                            "is_date_header": False, "is_error": True,
                            "Room no.": room_num, "Room name": room_name_err,
                            "Specification": "N/A",
                            "Analysis results": f"Error: {err_reason}"
                        })
                        continue

                    setpoint_row = setpoint_df[setpoint_df['Room_number'].astype(str) == room_num]
                    if setpoint_row.empty: continue
                                  
                    df = prepared_dfs_cache.get(room_num)
                    if df is None: continue
                    
                    # Verify corridor comparison data is present (ERR-011)
                    compare_room_val = setpoint_row['Room_Pressure_Comparison'].iloc[0] if 'Room_Pressure_Comparison' in setpoint_row.columns else None
                    if not pd.isna(compare_room_val) and str(compare_room_val).strip() != "" and str(compare_room_val) != room_num:
                        corr_room_id = str(compare_room_val)
                        if corr_room_id not in prepared_dfs_cache or prepared_dfs_cache[corr_room_id].empty:
                            audit_trail.log_event("ALARM_TRIGGERED", f"Action: analyze | Code: ERR-011 | Msg: Missing corridor data {corr_room_id} for Room {room_num}")
                            raise ValueError(f"ERR-011: Missing Corridor Data - Room {room_num} requires comparison with corridor room {corr_room_id}, but corridor data is missing.")
                    
                    res = _analyze_single_room_core(
                        df, 
                        room_num, 
                        setpoint_row, 
                        tick_mark, 
                        cross_mark, 
                        all_corridor_rooms, 
                        prepared_dfs_cache, 
                        selected_rooms, 
                        setpoint_df,
                        day_analysis_start,
                        day_analysis_end
                    )
                    if res is None: continue
                    spec_txt, analysis_res_txt = res
                    
                    report_data.append({
                        "is_date_header": False,
                        "Room no.": room_num, "Room name": setpoint_row['Room_name'].iloc[0],
                        "Specification": spec_txt, 
                        "Analysis results": analysis_res_txt
                    })
                    print(f"[{_day_idx}/{_total_day}] Completed Room: {room_num}\n--------------------")
                except Exception as e:
                    error_msg = f"ROOM ERROR [{room_num}]: {str(e)}"
                    print(error_msg)
                    traceback.print_exc(file=sys.stdout)
                    audit_trail.log_event("ROOM_ERROR", f"Room: {room_num} | Error: {str(e)}")
                    room_errors[room_num] = str(e)
                    try:
                        sp_row_err2 = setpoint_df[setpoint_df['Room_number'].astype(str) == room_num]
                        room_name_err2 = str(sp_row_err2['Room_name'].iloc[0]) if not sp_row_err2.empty and not pd.isna(sp_row_err2['Room_name'].iloc[0]) else "N/A"
                    except Exception:
                        room_name_err2 = "N/A"
                    report_data.append({
                        "is_date_header": False, "is_error": True,
                        "Room no.": room_num, "Room name": room_name_err2,
                        "Specification": "N/A",
                        "Analysis results": f"Error: {str(e)}"
                    })

        # --- Excel Export (wide day columns) ---
        output_path = os.path.join('reports', f"AQR_Report_{time.strftime('%Y%m%d_%H%M%S')}.xlsx")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        try:
            with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
                wb = writer.book
                ws = wb.add_worksheet('Report')

                fmt_header = wb.add_format({'font_name': 'Times New Roman', 'bold': True, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'bg_color': '#b0b0b0'})
                fmt_center = wb.add_format({'font_name': 'Times New Roman', 'border': 1, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True})
                fmt_left = wb.add_format({'font_name': 'Times New Roman', 'border': 1, 'align': 'left', 'valign': 'vcenter', 'text_wrap': True})
                fmt_top = wb.add_format({'font_name': 'Times New Roman', 'bold': True, 'font_size': 11, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'bg_color': '#b0b0b0'})
                fmt_error = wb.add_format({'font_name': 'Times New Roman', 'bold': True, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'text_wrap': True, 'bg_color': '#FFE0E0', 'font_color': '#CC0000'})
                fmt_error_center = wb.add_format({'font_name': 'Times New Roman', 'bold': True, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True, 'bg_color': '#FFE0E0', 'font_color': '#CC0000'})

                day_columns, room_rows = build_daily_wide_rows(report_data)
                headers = ["Room no.", "Room name", "Specification"] + day_columns
                last_col = len(headers) - 1

                if start_dt and end_dt:
                    ws.merge_range(0, 0, 0, max(2, last_col - 1), f'Period analyzed: {start_dt.strftime("%Y-%m-%d %H:%M")} to {end_dt.strftime("%Y-%m-%d %H:%M")}', fmt_top)

                # GAMP 5: UR-FN-08 Hardcode version and generation date (IQ-TC-01)
                ws.write(0, last_col, f'Software Version: v1.1.0\nGenerated: {time.strftime("%Y-%m-%d %H:%M")}', fmt_center)

                for col, val in enumerate(headers):
                    ws.write(1, col, val, fmt_header)

                ws.set_column('A:A', 12); ws.set_column('B:B', 35); ws.set_column('C:C', 25)
                for day_col_idx in range(3, len(headers)):
                    ws.set_column(day_col_idx, day_col_idx, 45)
                ws.freeze_panes(2, 3)

                current_row = 2
                for room_no in sorted(room_rows.keys()):
                    row = room_rows[room_no]
                    room_no_clean = clean_room_num_or_name(row["Room no."])
                    room_name_clean = clean_room_num_or_name(row["Room name"])
                    ws.write(current_row, 0, room_no_clean, fmt_center)
                    ws.write(current_row, 1, room_name_clean, fmt_left)
                    ws.write(current_row, 2, row["Specification"], fmt_left)

                    for day_col_idx, day_label in enumerate(day_columns, 3):
                        day_result = row["days"].get(day_label, "-")
                        is_error = isinstance(day_result, str) and day_result.strip().startswith("Error:")
                        ws.write(current_row, day_col_idx, day_result, fmt_error if is_error else fmt_left)
                    current_row += 1
        except Exception as excel_err:
            audit_trail.log_event("EXCEL_ERROR", f"Failed to write Excel report: {str(excel_err)}")
            raise ValueError(f"ERR-007: Report Generation Failed - {str(excel_err)}")

        # GAMP 5: UR-DI-01 Log Success and Report Identity
        report_name = os.path.basename(output_path)
        audit_trail.log_event("ANALYSIS_SUCCESS", f"Report: {report_name}")

        try:
            plot_result = _compute_plot_result(all_room_dfs, setpoint_df, list(selected_rooms), start_dt, end_dt)
            _summary = plot_result.get('summary', [])
            _n_errors = sum(1 for r in report_data if r.get('is_error'))
            plot_result['stats'] = {
                'total':      len(_summary) + _n_errors,
                'passed':     sum(1 for r in _summary if r['temp_v'] + r['hum_v'] + r['press_v'] == 0),
                'violations': sum(1 for r in _summary if r['temp_v'] + r['hum_v'] + r['press_v'] > 0),
                'errors':     _n_errors
            }
        except Exception as plot_err:
            audit_trail.log_event("PLOT_ERROR", f"Chart computation failed: {str(plot_err)}")
            plot_result = {"error": str(plot_err)}

        if isinstance(plot_result, dict):
            plot_result['room_errors'] = room_errors

        return output_path, log_stream.getvalue(), plot_result
    except Exception as e:
        print(f"ERROR: {str(e)}")
        traceback.print_exc(file=log_stream)
        audit_trail.log_event("ANALYSIS_FAILED", f"Error: {str(e)}")
        return None, log_stream.getvalue(), None
    finally: sys.stdout = old_stdout


# ============================================================
# PHASE 2 — EMS CSV (separate T/H/P files, semicolon-delimited)
# ============================================================

import glob as _glob

def prepare_df_phase2(raw_data_path, room_id=None, setpoint_df=None):
    """Read Phase 2 EMS CSV files (separate RMT/RMH/RDP) and merge into unified DataFrame.
    Returns (room_id, df) where df has columns: DateTime, Temperature, Humidity, Pressure.
    """
    def _find(suffix):
        found = []
        prefix = f"{room_id}_{suffix}_" if room_id else f"_{suffix}_"
        prefix_lower = prefix.lower()
        for root, _, files in os.walk(raw_data_path):
            for f in files:
                if f.lower().endswith('.csv'):
                    if room_id:
                        if f.lower().startswith(prefix_lower):
                            found.append(os.path.join(root, f))
                    else:
                        if f'_{suffix.upper()}_' in f.upper():
                            found.append(os.path.join(root, f))
        return sorted(found)

    rmt_files = _find('RMT')
    rmh_files = _find('RMH')
    rdp_files = _find('RDP')

    # Dynamic limits verification
    expected_params = {'Temperature'}
    if setpoint_df is not None and room_id is not None:
        row_sp = setpoint_df[setpoint_df['Room_number'].astype(str) == room_id]
        if not row_sp.empty:
            humidity_has_spec = (not pd.isna(row_sp['Humidity_Low_Limit'].iloc[0])) and (not pd.isna(row_sp['Humidity_High_Limit'].iloc[0]))
            if humidity_has_spec:
                expected_params.add('Humidity')
            pressure_has_spec = (not pd.isna(row_sp['Pressure_Low_Limit'].iloc[0])) and (not pd.isna(row_sp['Pressure_High_Limit'].iloc[0]))
            if pressure_has_spec:
                expected_params.add('Pressure')

    if not rmt_files:
        raise ValueError(f"ERR-005: No Temperature file (_RMT_) found in {raw_data_path} for {room_id}")
    if 'Humidity' in expected_params and not rmh_files:
        raise ValueError(f"ERR-005: No Humidity file (_RMH_) found in {raw_data_path} for {room_id}")
    if 'Pressure' in expected_params and not rdp_files:
        raise ValueError(f"ERR-005: No Pressure file (_RDP_) found in {raw_data_path} for {room_id}")

    # Room ID = prefix before '_RMT_' in the first RMT filename
    r_id = room_id if room_id else os.path.basename(rmt_files[0]).split('_RMT_')[0]

    def _read_files(file_list, col_name):
        dfs = []
        for f in file_list:
            try:
                df = pd.read_csv(
                    f, sep=';', skiprows=4, header=0,
                    usecols=[0, 2],  # DateTime=col0, Value=col2 (skip 'Data Source')
                    encoding='utf-8', encoding_errors='ignore'
                )
                df.columns = ['DateTime', col_name]
                df['DateTime'] = pd.to_datetime(df['DateTime'], dayfirst=True, errors='coerce')
                df = df.dropna(subset=['DateTime'])
                # Standardize DateTime index by rounding to nearest minute to eliminate seconds-drift
                df['DateTime'] = df['DateTime'].dt.round('min')
                df[col_name] = pd.to_numeric(df[col_name], errors='coerce')
                
                # Cut off the last row of every individual file to avoid next-day 00:00 duplication
                if len(df) > 1:
                    df = df.iloc[:-1]
                
                dfs.append(df[['DateTime', col_name]])
            except Exception as e:
                audit_trail.log_event("WARNING", f"Phase2 read error: {os.path.basename(f)} — {str(e)}")
        if not dfs:
            return pd.DataFrame(columns=['DateTime', col_name])
        result = pd.concat(dfs, ignore_index=True)
        if result['DateTime'].duplicated().any():
            dup_series = result[result['DateTime'].duplicated()]['DateTime'].dropna()
            if not dup_series.empty:
                dup_series_sorted = dup_series.sort_values()
                dup_count = len(dup_series_sorted)
                dup_start = dup_series_sorted.iloc[0].strftime('%Y-%m-%d %H:%M')
                dup_stop = dup_series_sorted.iloc[-1].strftime('%Y-%m-%d %H:%M')
                f_names = [os.path.basename(f) for f in file_list]
                warn_msg = f"[WARNING] ERR-008: Duplicate Timestamps Detected in Phase 2 {col_name} files: {f_names} for Room {r_id}. Found {dup_count:,} duplicate timestamps from {dup_start} to {dup_stop}. Dropping duplicates and keeping the first record."
                print(warn_msg)
                audit_trail.log_event("DUPLICATE_TIMESTAMPS_WARN", f"Room: {r_id} ({col_name}) | Files: {f_names} | Duplicates: {dup_count} records from {dup_start} to {dup_stop} | Action: Dropped subsequent records (ERR-008)")
        return result.drop_duplicates('DateTime').sort_values('DateTime').reset_index(drop=True)

    df_t = _read_files(rmt_files, 'Temperature')
    if df_t.empty:
        raise ValueError(f"ERR-005: No valid Temperature data parsed from {raw_data_path}")

    # Humidity optional — some rooms monitor temperature only
    if rmh_files:
        df_h = _read_files(rmh_files, 'Humidity')
        df = pd.merge(df_t, df_h, on='DateTime', how='outer').sort_values('DateTime').reset_index(drop=True)
    else:
        df = df_t.copy()
        df['Humidity'] = pd.NA

    # Pressure optional
    if rdp_files:
        df_p = _read_files(rdp_files, 'Pressure')
        df = pd.merge(df, df_p, on='DateTime', how='outer').sort_values('DateTime').reset_index(drop=True)
    else:
        df['Pressure'] = pd.NA

    df = df.reindex(columns=['DateTime', 'Temperature', 'Humidity', 'Pressure'])
    sensors = {'Temperature'}
    if rmh_files: sensors.add('Humidity')
    if rdp_files: sensors.add('Pressure')
    return r_id, df, sensors


def scan_phase2_rooms(folder_path):
    """Recursively walk folder tree looking for any directory that contains _RMT_/_RMH_/_RDP_ files.
    Returns {room_id: dir_path} regardless of how deep the Raw Data folder is.
    """
    room_map = {}
    for root, dirs, files in os.walk(folder_path):
        for f in files:
            if f.lower().endswith('.csv'):
                for suffix in ['_RMT_', '_RMH_', '_RDP_']:
                    if suffix in f:
                        room_id = f.split(suffix)[0]
                        if room_id not in room_map:
                            room_map[room_id] = folder_path
                        break
    return room_map


def get_file_date_range_phase2(raw_data_path, room_id=None):
    """Get combined date range from all CSV files in a Phase 2 folder (any depth)."""
    all_dates = []
    all_files = []
    suffixes = ['_RMT_', '_RMH_', '_RDP_']
    for root, _, files in os.walk(raw_data_path):
        for f in files:
            if f.lower().endswith('.csv'):
                for suffix in suffixes:
                    prefix = f"{room_id}{suffix}" if room_id else suffix
                    if prefix.lower() in f.lower():
                        all_files.append(os.path.join(root, f))
                        break
    for f in all_files:
        try:
            df = pd.read_csv(f, sep=';', skiprows=4, header=0,
                             usecols=[0], encoding='utf-8', encoding_errors='ignore')
            df.columns = ['DateTime']
            df['DateTime'] = pd.to_datetime(df['DateTime'], dayfirst=True, errors='coerce')
            # Standardize DateTime by rounding to nearest minute (consistent with _read_files)
            df['DateTime'] = df['DateTime'].dt.round('min')
            # Drop footer/invalid rows first (consistent with _read_files)
            df = df.dropna()
            # Then cut off the last data row to avoid next-day 00:00 duplication (consistent with _read_files)
            if len(df) > 1:
                df = df.iloc[:-1]
            if not df.empty:
                all_dates.append(df['DateTime'].min().date())
                all_dates.append(df['DateTime'].max().date())
        except Exception:
            continue
    if not all_dates:
        return None, None
    return min(all_dates), max(all_dates)


def analyze_files_phase2(folder_path, setpoint_path, selected_rooms=None, start_date=None, end_date=None, log_queue=None):
    """Phase 2 analysis — reads EMS CSV (RMT/RMH/RDP) files per room, runs same logic as Phase 1."""
    old_stdout = sys.stdout
    sys.stdout = log_stream = QueueWriter(log_queue)
    try:
        try:
            setpoint_df = pd.read_excel(setpoint_path)
        except FileNotFoundError:
            raise ValueError("ERR-002: Limit File Not Found")

        required_cols = ['Room_number', 'Temperature_Limit', 'Humidity_Low_Limit', 'Humidity_High_Limit', 'Pressure_Low_Limit', 'Pressure_High_Limit']
        missing_cols = [col for col in required_cols if col not in setpoint_df.columns]
        if missing_cols:
            raise ValueError(f"ERR-009: Invalid Limit File Format - Missing required columns: {', '.join(missing_cols)}")

        all_corridor_rooms = set(setpoint_df['Room_Pressure_Comparison'].dropna().astype(str).unique()) if 'Room_Pressure_Comparison' in setpoint_df.columns else set()
        needed_rooms = set(selected_rooms) if selected_rooms else set()
        if selected_rooms:
            for r in selected_rooms:
                sp_row = setpoint_df[setpoint_df['Room_number'].astype(str) == r]
                if not sp_row.empty and 'Room_Pressure_Comparison' in setpoint_df.columns:
                    comp_val = sp_row['Room_Pressure_Comparison'].iloc[0]
                    if not pd.isna(comp_val):
                        needed_rooms.add(str(comp_val))

        tick_mark, cross_mark = 'Passed', 'Out of spec'
        start_dt = pd.to_datetime(start_date).tz_localize(None) if start_date else None
        end_dt   = pd.to_datetime(end_date).tz_localize(None)   if end_date   else None

        limit_hash = get_file_hash(setpoint_path)
        audit_trail.log_event("ANALYSIS_START", f"Folder: {folder_path} | Limit_Hash: {limit_hash}")

        room_errors = {}

        # --- Scan all rooms in folder tree ---
        room_scan = scan_phase2_rooms(folder_path)  # {room_id: raw_data_path}

        # --- Load all selected/needed rooms upfront ---
        room_full_dfs  = {}   # {room_id: full_range_df}
        room_sensors   = {}   # {room_id: set of available sensor names}
        room_files     = {}   # {room_id: [list of file info dicts]}
        failed_rooms   = {}   # {room_id: error_msg}

        for room_id, raw_data_path in room_scan.items():
            if needed_rooms and room_id not in needed_rooms:
                continue
            if setpoint_df[setpoint_df['Room_number'].astype(str) == room_id].empty:
                continue
            try:
                _, df, sensors = prepare_df_phase2(raw_data_path, room_id=room_id, setpoint_df=setpoint_df)
                room_full_dfs[room_id] = df
                room_sensors[room_id]  = sensors
                # Gather all files of interest (RMT, RMH, RDP)
                room_files[room_id] = []
                all_files = []
                for root, _, files in os.walk(raw_data_path):
                    for f in files:
                        f_lower = f.lower()
                        is_target = False
                        for suffix in ['_rmt_', '_rmh_', '_rdp_']:
                            if f_lower.startswith(f"{room_id.lower()}{suffix}") and f_lower.endswith('.csv'):
                                is_target = True
                                break
                        if is_target:
                            all_files.append(os.path.join(root, f))
                for f_path in sorted(all_files):
                    start_d, end_d = get_file_date_range(f_path)
                    f_hash = get_file_hash(f_path)
                    room_files[room_id].append({
                        'name': os.path.basename(f_path),
                        'start': start_d,
                        'end': end_d,
                        'hash': f_hash
                    })
            except Exception as e:
                error_msg = f"FILE ERROR [{room_id}]: {str(e)}"
                print(error_msg)
                traceback.print_exc(file=sys.stdout)
                audit_trail.log_event("FILE_ERROR", f"Room: {room_id} | Error: {str(e)}")
                failed_rooms[room_id] = str(e)

        # GxP Upfront Validation: Verify all selected rooms have valid, complete folders and files (ERR-005)
        for room_id in (selected_rooms or []):
            if setpoint_df[setpoint_df['Room_number'].astype(str) == room_id].empty:
                continue
            
            # Check folder existence
            if room_id not in room_scan:
                raise ValueError(f"ERR-005: Raw data folder not found in {folder_path} for Room {room_id}")
            
            # Check file presence and completeness
            raw_data_path = room_scan[room_id]
            if room_id in failed_rooms:
                err_msg = failed_rooms[room_id]
                if not err_msg.startswith("ERR-"):
                    raise ValueError(f"ERR-005: Error parsing Room {room_id}: {err_msg}")
                raise ValueError(err_msg)
            
            if room_id not in room_full_dfs:
                raise ValueError(f"ERR-005: Raw data files not found in {raw_data_path} for Room {room_id}")

        if not room_full_dfs and not failed_rooms:
            audit_trail.log_event("ANALYSIS_FAILED", "ERR-010: No Matching Files Found matching criteria.")
            raise ValueError("ERR-010: No Matching Files Found matching criteria.")

        report_data = []
        all_room_dfs = {}  # for chart — accumulate day-filtered slices

        # --- Day-by-day loop (consistent with Phase 1 report format) ---
        for current_date in pd.date_range(start_dt.date(), end_dt.date()):
            day_start = pd.Timestamp(current_date).tz_localize(None)
            day_end   = day_start + pd.Timedelta(hours=23, minutes=55)
            day_analysis_start = max(day_start, start_dt)
            day_analysis_end = min(day_end, end_dt)

            # Build day-filtered cache for analysis and corridor comparison
            day_cache = {}
            for room_id, full_df in room_full_dfs.items():
                day_df = full_df[(full_df['DateTime'] >= day_start) & (full_df['DateTime'] <= day_end)].copy().reset_index(drop=True)
                if not day_df.empty:
                    day_cache[room_id] = day_df
                    all_room_dfs.setdefault(room_id, []).append(day_df)

            rooms_for_day = [r for r in (selected_rooms or []) if r in day_cache or r in failed_rooms]
            if not rooms_for_day:
                continue

            print(f"\n============================================================")
            print(f" DATE: {current_date.strftime('%Y-%m-%d')}")
            print(f"============================================================\n")
            # Prefer actual data time span from day cache; fallback to analysis window.
            actual_day_start = day_analysis_start
            actual_day_end = day_analysis_end
            if day_cache:
                actual_day_start = min(df['DateTime'].min() for df in day_cache.values() if not df.empty)
                actual_day_end = max(df['DateTime'].max() for df in day_cache.values() if not df.empty)
            report_data.append({
                "is_date_header": True,
                "date_text": f"DATE: {current_date.strftime('%Y-%m-%d')}",
                "day_column_label": f"{current_date.strftime('%Y-%m-%d')} ({actual_day_start.strftime('%H:%M')}-{actual_day_end.strftime('%H:%M')})"
            })

            # Log all processed files for needed rooms on this day (consistent with Phase 1)
            for r_id in sorted(needed_rooms):
                if r_id in day_cache and r_id in room_files:
                    for f_info in room_files[r_id]:
                        if f_info['start'] and f_info['start'] == current_date.date():
                            audit_trail.log_event("FILE_PROCESSED", f"Room: {r_id} | File: {f_info['name']} | SHA256: {f_info['hash']}")

            _total_day = len(rooms_for_day)
            for _day_idx, room_num in enumerate(rooms_for_day, 1):
                # --- Error from loading stage ---
                if room_num in failed_rooms:
                    sp_err = setpoint_df[setpoint_df['Room_number'].astype(str) == room_num]
                    rname_err = str(sp_err['Room_name'].iloc[0]) if not sp_err.empty and not pd.isna(sp_err['Room_name'].iloc[0]) else "N/A"
                    print(f"[ERROR] Skipping Room {room_num} ({rname_err}): {failed_rooms[room_num]}")
                    audit_trail.log_event("ROOM_SKIPPED_ERROR", f"Room: {room_num} | Reason: {failed_rooms[room_num]}")
                    room_errors[room_num] = failed_rooms[room_num]
                    report_data.append({
                        "is_date_header": False, "is_error": True,
                        "Room no.": room_num, "Room name": rname_err,
                        "Specification": "N/A",
                        "Analysis results": f"Error: {failed_rooms[room_num]}"
                    })
                    continue

                try:
                    print(f"[{_day_idx}/{_total_day}] Processing Room: {room_num}")
                    setpoint_row = setpoint_df[setpoint_df['Room_number'].astype(str) == room_num]
                    if setpoint_row.empty:
                        continue
                    
                    df = day_cache.get(room_num)
                    if df is None:
                        continue
                    
                    # Verify corridor comparison data is present (ERR-011)
                    compare_room_val = setpoint_row['Room_Pressure_Comparison'].iloc[0] if 'Room_Pressure_Comparison' in setpoint_row.columns else None
                    if not pd.isna(compare_room_val) and str(compare_room_val).strip() != "" and str(compare_room_val) != room_num:
                        corr_room_id = str(compare_room_val)
                        if corr_room_id not in day_cache or day_cache[corr_room_id].empty:
                            audit_trail.log_event("ALARM_TRIGGERED", f"Action: analyze | Code: ERR-011 | Msg: Missing corridor data {corr_room_id} for Room {room_num}")
                            raise ValueError(f"ERR-011: Missing Corridor Data - Room {room_num} requires comparison with corridor room {corr_room_id}, but corridor data is missing.")
                    
                    res = _analyze_single_room_core(
                        df, 
                        room_num, 
                        setpoint_row, 
                        tick_mark, 
                        cross_mark, 
                        all_corridor_rooms, 
                        day_cache, 
                        selected_rooms, 
                        setpoint_df,
                        day_analysis_start,
                        day_analysis_end
                    )
                    if res is None: continue
                    spec_txt, analysis_res_txt = res
                    
                    report_data.append({
                        "is_date_header": False,
                        "Room no.": room_num, "Room name": setpoint_row['Room_name'].iloc[0],
                        "Specification": spec_txt,
                        "Analysis results": analysis_res_txt
                    })
                    print(f"[{_day_idx}/{_total_day}] Completed Room: {room_num}\n--------------------")

                except Exception as e:
                    error_msg = f"ROOM ERROR [{room_num}]: {str(e)}"
                    print(error_msg)
                    traceback.print_exc(file=sys.stdout)
                    audit_trail.log_event("ROOM_ERROR", f"Room: {room_num} | Error: {str(e)}")
                    room_errors[room_num] = str(e)
                    try:
                        sp_err2 = setpoint_df[setpoint_df['Room_number'].astype(str) == room_num]
                        rname_err2 = str(sp_err2['Room_name'].iloc[0]) if not sp_err2.empty and not pd.isna(sp_err2['Room_name'].iloc[0]) else "N/A"
                    except Exception:
                        rname_err2 = "N/A"
                    report_data.append({
                        "is_date_header": False, "is_error": True,
                        "Room no.": room_num, "Room name": rname_err2,
                        "Specification": "N/A",
                        "Analysis results": f"Error: {str(e)}"
                    })

        # --- Excel Export (wide day columns) ---
        output_path = os.path.join('reports', f"AQR_Report_P2_{time.strftime('%Y%m%d_%H%M%S')}.xlsx")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        try:
            with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
                wb = writer.book
                ws = wb.add_worksheet('Report')
                fmt_header      = wb.add_format({'font_name': 'Times New Roman', 'bold': True, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'bg_color': '#b0b0b0'})
                fmt_center      = wb.add_format({'font_name': 'Times New Roman', 'border': 1, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True})
                fmt_left        = wb.add_format({'font_name': 'Times New Roman', 'border': 1, 'align': 'left',   'valign': 'vcenter', 'text_wrap': True})
                fmt_top         = wb.add_format({'font_name': 'Times New Roman', 'bold': True, 'font_size': 11, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'bg_color': '#b0b0b0'})
                fmt_error       = wb.add_format({'font_name': 'Times New Roman', 'bold': True, 'border': 1, 'align': 'left',   'valign': 'vcenter', 'text_wrap': True, 'bg_color': '#FFE0E0', 'font_color': '#CC0000'})
                fmt_error_center= wb.add_format({'font_name': 'Times New Roman', 'bold': True, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True, 'bg_color': '#FFE0E0', 'font_color': '#CC0000'})
                day_columns, room_rows = build_daily_wide_rows(report_data)
                headers = ["Room no.", "Room name", "Specification"] + day_columns
                last_col = len(headers) - 1
                if start_dt and end_dt:
                    ws.merge_range(0, 0, 0, max(2, last_col - 1), f'Period analyzed: {start_dt.strftime("%Y-%m-%d %H:%M")} to {end_dt.strftime("%Y-%m-%d %H:%M")}', fmt_top)
                ws.write(0, last_col, f'Software Version: v1.1.0\nGenerated: {time.strftime("%Y-%m-%d %H:%M")}', fmt_center)
                for col, val in enumerate(headers):
                    ws.write(1, col, val, fmt_header)
                ws.set_column('A:A', 12); ws.set_column('B:B', 35); ws.set_column('C:C', 25)
                for day_col_idx in range(3, len(headers)):
                    ws.set_column(day_col_idx, day_col_idx, 45)
                ws.freeze_panes(2, 3)
                current_row = 2
                for room_no in sorted(room_rows.keys()):
                    row = room_rows[room_no]
                    room_no_clean = clean_room_num_or_name(row["Room no."])
                    room_name_clean = clean_room_num_or_name(row["Room name"])
                    ws.write(current_row, 0, room_no_clean, fmt_center)
                    ws.write(current_row, 1, room_name_clean, fmt_left)
                    ws.write(current_row, 2, row["Specification"], fmt_left)
                    for day_col_idx, day_label in enumerate(day_columns, 3):
                        day_result = row["days"].get(day_label, "-")
                        is_error = isinstance(day_result, str) and day_result.strip().startswith("Error:")
                        ws.write(current_row, day_col_idx, day_result, fmt_error if is_error else fmt_left)
                    current_row += 1
        except Exception as excel_err:
            audit_trail.log_event("EXCEL_ERROR", f"Failed to write Excel report: {str(excel_err)}")
            raise ValueError(f"ERR-007: Report Generation Failed - {str(excel_err)}")

        report_name = os.path.basename(output_path)
        audit_trail.log_event("ANALYSIS_SUCCESS", f"Report: {report_name}")

        try:
            plot_result = _compute_plot_result(all_room_dfs, setpoint_df, list(selected_rooms), start_dt, end_dt)
            _summary = plot_result.get('summary', [])
            _n_errors = sum(1 for r in report_data if r.get('is_error'))
            plot_result['stats'] = {
                'total':      len(_summary) + _n_errors,
                'passed':     sum(1 for r in _summary if r['temp_v'] + r['hum_v'] + r['press_v'] == 0),
                'violations': sum(1 for r in _summary if r['temp_v'] + r['hum_v'] + r['press_v'] > 0),
                'errors':     _n_errors
            }
        except Exception as plot_err:
            audit_trail.log_event("PLOT_ERROR", f"Chart computation failed: {str(plot_err)}")
            plot_result = {"error": str(plot_err)}

        if isinstance(plot_result, dict):
            plot_result['room_errors'] = room_errors

        return output_path, log_stream.getvalue(), plot_result

    except Exception as e:
        print(f"ERROR: {str(e)}")
        traceback.print_exc(file=log_stream)
        audit_trail.log_event("ANALYSIS_FAILED", f"Error: {str(e)}")
        return None, log_stream.getvalue(), None
    finally:
        sys.stdout = old_stdout
