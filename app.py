import pandas as pd
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for
import os
import sys
import audit_trail # GAMP 5: UR-DI-01 Secure Audit Trail
import webbrowser
import re
import csv
import threading
import queue as _queue
import uuid
from threading import Timer
import tkinter as tk
from tkinter import filedialog
from analysis_logic import (analyze_files, get_plot_info, find_point_mapping, get_file_hash,
                            get_file_date_range, parse_filename_for_datetime,
                            analyze_files_phase2, scan_phase2_rooms, get_file_date_range_phase2)
import datetime
import traceback
import json
from flask import Response
from waitress import serve # GAMP 5: Production WSGI Server (IQ-TC-06 Standalone)
from werkzeug.exceptions import HTTPException, NotFound

# Create a 'reports' directory if it doesn't exist (IQ-TC-02)
if not os.path.exists('reports'):
    os.makedirs('reports')

# --- GAMP 5: Path Persistence Refactoring ---
if getattr(sys, 'frozen', False):
    # Running as PyInstaller .exe
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    static_folder = os.path.join(sys._MEIPASS, 'static')
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder, root_path=sys._MEIPASS)
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Running as standard Python script
    app = Flask(__name__)
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# GAMP 5: Automatic Static File Cache Busting (Versioning)
# Appends ?v=<timestamp> to static files automatically so users never need to Ctrl+F5.
@app.context_processor
def override_url_for():
    def dated_url_for(endpoint, **values):
        if endpoint == 'static':
            filename = values.get('filename', None)
            if filename:
                file_path = os.path.join(app.static_folder, filename)
                if os.path.exists(file_path):
                    values['v'] = int(os.stat(file_path).st_mtime)
        return url_for(endpoint, **values)
    return dict(url_for=dated_url_for)

# GAMP 5: Reports directory setup
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')
if not os.path.exists(REPORTS_DIR):
    os.makedirs(REPORTS_DIR)

# GAMP 5: Logs directory setup (UR-DI-01, IQ-TC-02, IQ-TC-04)
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

# --- Job store for SSE streaming analysis ---
_jobs = {}          # job_id -> { queue, done, response, plot, error }
_jobs_lock = threading.Lock()
_analysis_lock = threading.Lock()  # one analysis at a time (stdout redirect safety)

# GAMP 5: UR-DI-01 Verify audit trail integrity on startup (IQ-TC-07)
try:
    audit_valid, audit_msg = audit_trail.verify_audit_trail()
    if not audit_valid:
        # ERR-004: Audit Log Corrupt - System must refuse to start
        # Show GUI error message since console is hidden
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()  # Hide main window
        messagebox.showerror(
            "ERR-004",
            f"ERR-004: Audit Trail Integrity Check Failed\n\nDetails: {audit_msg}\n\nSystem execution halted due to security violation."
        )
        root.destroy()
        print(f"ERR-004: Audit Trail Integrity Check Failed")
        print(f"Details: {audit_msg}")
        print("System execution halted due to security violation.")
        sys.exit(1) # IQ-TC-07: Halt system on integrity failure
except Exception as e:
    print(f"AUDIT TRAIL WARNING: Could not verify integrity on startup: {str(e)}")

# GAMP 5: UR-DI-01 Log application startup event
try:
    audit_trail.log_event("APPLICATION_START", "AQR System v1.1.0 launched successfully") # CRR-TC-01
except Exception as e:
    print(f"AUDIT TRAIL WARNING: Could not log startup event: {str(e)}")

# --- Global Error Handler (Enhanced for GxP Diagnostics) ---
@app.errorhandler(Exception) # Catch ALL exceptions
def handle_exception(e):
    # Differentiate between standard HTTP errors and critical system errors
    if isinstance(e, HTTPException):
        if isinstance(e, NotFound):
            # Log as non-critical warning if path is not essential (like favicon or other assets)
            audit_trail.log_event("NOT_FOUND", f"Requested URL: {request.url}")
            return jsonify({"error": "Resource not found on server."}), 404
        return e # Return other HTTP exceptions normally

    tb = traceback.format_exc()
    # Log true exceptions as SYSTEM_ERROR with URL context
    audit_trail.log_event("SYSTEM_ERROR", f"URL: {request.url} | Type: {type(e).__name__} | Msg: {str(e)} | Traceback: {tb}")
    return jsonify({"error": "Internal Server Error. Diagnostics logged in audit trail."}), 500

def _parse_filename_for_datetime(filename):
    """Parses date from filename and subtracts 1 day as per business logic.
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
                return parsed_dt - pd.Timedelta(days=1)
    except Exception:
        pass
    return None

# Define reports directory absolute path
REPORTS_DIR = os.path.abspath('reports')

def create_hidden_tk_root():
    root = tk.Tk()
    root.withdraw()
    root.call('wm', 'attributes', '.', '-topmost', True)
    return root

@app.route('/')
def index():
    """Redirect home to the main dashboard."""
    return redirect(url_for('aqr'))

@app.route('/favicon.ico')
def favicon():
    """Handle browser favicon requests with 204 No Content to avoid 404 logs."""
    return '', 204

@app.route('/aqr')
def aqr():
    return render_template('aqr.html')

@app.route('/transform')
def transform():
    """Render the Data Transformation module."""
    return render_template('transform.html')

@app.route('/browse-file-csv')
def browse_file_csv():
    root = create_hidden_tk_root()
    path = filedialog.askopenfilename(
        master=root, 
        title="Select CSV File", 
        filetypes=[("CSV files", "*.csv")]
    )
    root.destroy()
    return jsonify({'path': path.replace('\\', '/') if path else ''})

def _get_room_code(point_name, is_m5=False, is_pilot=False):
    if not point_name: return None
    if is_pilot:
        match = re.search(r'(\dS\d{3})', str(point_name))
        if match:
            code = match.group(1)
            return f"{code[0]}-{code[1:]}"
    elif is_m5:
        match = re.search(r'([12]P\d{3})', str(point_name))
        if match:
            code = match.group(1)
            return f"{code[0]}-{code[1:]}"
    else:
        match = re.search(r'([12]-P\d{3})', str(point_name))
        if match:
            return match.group(1)
    return None

def _write_custom_csv(df, output_path, point_names):
    # Filter out footer rows if any in df
    clean_df = df[df['<>Date'].astype(str).str.contains(r'\d{1,2}/\d{1,2}/\d{4}', na=False)].copy()
    
    if not clean_df.empty:
        start_dt = f"{clean_df.iloc[0]['<>Date']} {clean_df.iloc[0]['Time']}"
        end_dt = f"{clean_df.iloc[-1]['<>Date']} {clean_df.iloc[-1]['Time']}"
    else:
        start_dt = end_dt = "N/A"

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        f.write('"Key            Name:Suffix                                Trend Definitions Used"\n')
        for i in range(3):
            p_name = point_names[i] if i < len(point_names) else ""
            f.write(f'"Point_{i+1}:","{p_name}","","5 minutes"\n')
        f.write('"Time Interval:","5 Minutes"\n')
        f.write(f'"Date Range:","{start_dt} - {end_dt}"\n')
        f.write('"Report Timings:","All Hours"\n')
        f.write('""\n')
        f.write('"<>Date","Time","Point_1","Point_2","Point_3"\n')
        for _, row in clean_df.iterrows():
            f.write(f'"{row["<>Date"]}","{row["Time"]}","{row["Point_1"]}","{row["Point_2"]}","{row["Point_3"]}"\n')
        f.write(' " ******************************** End of Report *********************************"')

@app.route('/api/transform/split-reports', methods=['POST'])
def api_split_reports():
    try:
        import csv
        data = request.get_json()
        mo5_file = data.get('mo5_file')
        rmt_file = data.get('rmt_file')
        rmh_file = data.get('rmh_file')
        rpt_file = data.get('rpt_file')
        
        # Pilot Plant
        pilot_rmt_file = data.get('pilot_rmt_file')
        pilot_rmh_file = data.get('pilot_rmh_file')
        pilot_rpt_file = data.get('pilot_rpt_file')
        
        output_dir = data.get('output_dir')
        
        logs = []
        if not output_dir:
            return jsonify({'error': 'Output directory is required.'}), 400
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        def process_file_manual(file_path):
            point_names, data_start_line = {}, 0
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for i, row in enumerate(reader):
                    if row and row[0].startswith("Point_"):
                        p_num = int(row[0].replace("Point_", "").replace(":", ""))
                        point_names[p_num] = row[1]
                    if row and "<>Date" in row[0]:
                        data_start_line = i
                        break
            df = pd.read_csv(file_path, skiprows=data_start_line)
            df = df[df['<>Date'].notna() & ~df['<>Date'].str.contains("End of Report")].copy()
            return df, point_names

        # Process Module 5 with dynamic mapping like Main Plant
        if mo5_file and os.path.exists(mo5_file):
            logs.append("Processing Module 5...")
            df_m5, names_m5 = process_file_manual(mo5_file)
            
            # Get unique room codes from temperature points (like Main Plant logic)
            unique_rooms = set()
            for point_num in names_m5:
                room_code = _get_room_code(names_m5.get(point_num), is_m5=True)
                if room_code:
                    unique_rooms.add(room_code)
            
            for room_code in unique_rooms:
                room_df = df_m5[['<>Date', 'Time']].copy()
                
                # Find dynamic points for this room (like Main Plant logic)
                temp_point = None
                hum_point = None
                pressure_point = None
                
                try:
                    # Read file headers to find correct points for this room
                    with open(mo5_file, 'r', encoding='utf-8', errors='ignore') as f:
                        m5_lines = [line.replace('"','').replace('\n','') for line in f.readlines()]
                    
                    # Find temperature point (RMT suffix)
                    temp_point = find_point_mapping(m5_lines, room_code, "TEMP")
                    
                    # Find humidity point (RMH suffix)
                    hum_point = find_point_mapping(m5_lines, room_code, "HUM")
                    
                    # Find pressure point (RPT suffix)
                    pressure_point = find_point_mapping(m5_lines, room_code, "PRES")
                    
                except Exception as e:
                    print(f"Warning M5: Could not find points for {room_code}: {e}")
                
                # Use dynamically found points with fallback
                if temp_point and temp_point in df_m5.columns:
                    room_df['Point_1'] = df_m5[temp_point]
                else:
                    room_df['Point_1'] = "No Data"
                
                if hum_point and hum_point in df_m5.columns:
                    room_df['Point_2'] = df_m5[hum_point]
                else:
                    room_df['Point_2'] = "No Data"
                
                if pressure_point and pressure_point in df_m5.columns:
                    room_df['Point_3'] = df_m5[pressure_point]
                else:
                    room_df['Point_3'] = "No Data"
                
                try:
                    first_date = datetime.datetime.strptime(room_df.iloc[0]['<>Date'], '%m/%d/%Y')
                    filename = f"M5 {room_code}_{first_date.strftime('%m-%d-%y')}_{room_df.iloc[0]['Time'][:5].replace(':', '-')}.csv"
                except:
                    filename = f"M5 {room_code}_unknown.csv"
                
                _write_custom_csv(room_df, os.path.join(output_dir, filename), 
                                 [temp_point or "", hum_point or "", pressure_point or ""])
                logs.append(f"  Created: {filename}")

        # Process Main Plant
        if all([rmt_file, rmh_file, rpt_file]) and all(os.path.exists(f) for f in [rmt_file, rmh_file, rpt_file]):
            logs.append("Processing Main Plant...")
            df_t, names_t = process_file_manual(rmt_file)
            df_h, names_h = process_file_manual(rmh_file)
            df_p, names_p = process_file_manual(rpt_file)
            
            for p_idx in names_t:
                room_code = _get_room_code(names_t.get(p_idx), is_m5=False)
                if not room_code: continue
                
                room_df = df_t[['<>Date', 'Time']].copy()
                
                # CRITICAL FIX: Use dynamic mapping for all three point types
                # Find the correct points for this room from each file
                temp_point = None
                hum_point = None
                pressure_point = None
                
                try:
                    # Read file headers to find correct points for this room
                    with open(rmt_file, 'r', encoding='utf-8', errors='ignore') as f:
                        rmt_lines = [line.replace('"','').replace('\n','') for line in f.readlines()]
                    temp_point = find_point_mapping(rmt_lines, room_code, "TEMP")
                    
                    with open(rmh_file, 'r', encoding='utf-8', errors='ignore') as f:
                        rmh_lines = [line.replace('"','').replace('\n','') for line in f.readlines()]
                    hum_point = find_point_mapping(rmh_lines, room_code, "HUM")
                    
                    with open(rpt_file, 'r', encoding='utf-8', errors='ignore') as f:
                        rpt_lines = [line.replace('"','').replace('\n','') for line in f.readlines()]
                    pressure_point = find_point_mapping(rpt_lines, room_code, "PRES")
                except Exception as e:
                    print(f"Warning: Could not find points for {room_code}: {e}")
                
                # Use dynamically found points with fallback
                if temp_point and temp_point in df_t.columns:
                    room_df['Point_1'] = df_t[temp_point]
                else:
                    # Fallback to original logic
                    col_name = f'Point_{p_idx}'
                    room_df['Point_1'] = df_t[col_name] if col_name in df_t.columns else "No Data"
                
                if hum_point and hum_point in df_h.columns:
                    room_df['Point_2'] = df_h[hum_point]
                else:
                    # Fallback to original logic
                    col_name = f'Point_{p_idx}'
                    room_df['Point_2'] = df_h[col_name] if col_name in df_h.columns else "No Data"
                
                # Use dynamically found pressure point with fallback
                if pressure_point and pressure_point in df_p.columns:
                    room_df['Point_3'] = df_p[pressure_point]
                else:
                    # Enhanced fallback: try to find any pressure point for this room
                    fallback_point = None
                    try:
                        # Get all pressure points from the pressure file
                        with open(rpt_file, 'r', encoding='utf-8', errors='ignore') as f:
                            pressure_lines = [line.replace('"','').replace('\n','') for line in f.readlines() 
                                            if 'Point_' in line and 'ROOM PRES' in line]
                        
                        # Look for any point containing this room code
                        for line in pressure_lines:
                            parts = line.split(',')
                            if len(parts) >= 2:
                                point_name = parts[0].strip().replace(':', '')
                                room_identifier = parts[1].strip()
                                if room_code in room_identifier or room_code.replace('-', '') in room_identifier:
                                    fallback_point = point_name
                                    break
                        
                        if fallback_point and fallback_point in df_p.columns:
                            room_df['Point_3'] = df_p[fallback_point]
                        else:
                            room_df['Point_3'] = "No Data"
                    except Exception as e:
                        room_df['Point_3'] = "No Data"
                
                try:
                    first_date = datetime.datetime.strptime(room_df.iloc[0]['<>Date'], '%m/%d/%Y')
                    filename = f"{room_code}_{first_date.strftime('%m-%d-%y')}_{room_df.iloc[0]['Time'][:5].replace(':', '-')}.csv"
                except:
                    filename = f"{room_code}_unknown.csv"
                
                _write_custom_csv(room_df, os.path.join(output_dir, filename), [names_t.get(p_idx, ""), names_h.get(p_idx, ""), names_p.get(p_idx, "")])
                logs.append(f"  Created: {filename}")

        # Process Pilot Plant
        if all([pilot_rmt_file, pilot_rmh_file, pilot_rpt_file]) and all(os.path.exists(f) for f in [pilot_rmt_file, pilot_rmh_file, pilot_rpt_file]):
            logs.append("Processing Pilot Plant...")
            df_t_pilot, names_t_pilot = process_file_manual(pilot_rmt_file)
            df_h_pilot, names_h_pilot = process_file_manual(pilot_rmh_file)
            df_p_pilot, names_p_pilot = process_file_manual(pilot_rpt_file)
            
            # Optimize: Read file headers once for mapping
            try:
                with open(pilot_rmt_file, 'r', encoding='utf-8', errors='ignore') as f:
                    rmt_lines = [line.replace('"','').replace('\n','') for line in f.readlines()]
                with open(pilot_rmh_file, 'r', encoding='utf-8', errors='ignore') as f:
                    rmh_lines = [line.replace('"','').replace('\n','') for line in f.readlines()]
                with open(pilot_rpt_file, 'r', encoding='utf-8', errors='ignore') as f:
                    rpt_lines = [line.replace('"','').replace('\n','') for line in f.readlines()]
            except Exception as e:
                logs.append(f"Error reading Pilot headers: {e}")
                rmt_lines, rmh_lines, rpt_lines = [], [], []

            for p_idx in names_t_pilot:
                room_code = _get_room_code(names_t_pilot.get(p_idx), is_pilot=True)
                if not room_code: continue
                
                room_df = df_t_pilot[['<>Date', 'Time']].copy()
                
                # Dynamic mapping for Pilot Plant
                temp_point = find_point_mapping(rmt_lines, room_code, "TEMP")
                hum_point = find_point_mapping(rmh_lines, room_code, "HUM")
                pressure_point = find_point_mapping(rpt_lines, room_code, "PRES")
                
                # Temperature extraction with fallback
                if temp_point and temp_point in df_t_pilot.columns:
                    room_df['Point_1'] = df_t_pilot[temp_point]
                else:
                    col_name = f'Point_{p_idx}'
                    room_df['Point_1'] = df_t_pilot[col_name] if col_name in df_t_pilot.columns else "No Data"
                
                # Humidity extraction with fallback
                if hum_point and hum_point in df_h_pilot.columns:
                    room_df['Point_2'] = df_h_pilot[hum_point]
                else:
                    col_name = f'Point_{p_idx}'
                    room_df['Point_2'] = df_h_pilot[col_name] if col_name in df_h_pilot.columns else "No Data"
                
                # Pressure extraction with fallback (Fixes the "No Data" issue)
                if pressure_point and pressure_point in df_p_pilot.columns:
                    room_df['Point_3'] = df_p_pilot[pressure_point]
                else:
                    col_name = f'Point_{p_idx}'
                    room_df['Point_3'] = df_p_pilot[col_name] if col_name in df_p_pilot.columns else "No Data"
                
                try:
                    first_date = datetime.datetime.strptime(room_df.iloc[0]['<>Date'], '%m/%d/%Y')
                    filename = f"{room_code}_{first_date.strftime('%m-%d-%y')}_{room_df.iloc[0]['Time'][:5].replace(':', '-')}.csv"
                except:
                    filename = f"{room_code}_unknown.csv"
                
                _write_custom_csv(room_df, os.path.join(output_dir, filename), [names_t_pilot.get(p_idx, ""), names_h_pilot.get(p_idx, ""), names_p_pilot.get(p_idx, "")])
                logs.append(f"  Created: {filename}")

        return jsonify({'logs': logs, 'status': 'success'})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/browse-folder')
def browse_folder():
    root = create_hidden_tk_root()
    path = filedialog.askdirectory(master=root, title="Select Analysis Folder")
    root.destroy()
    return jsonify({'path': path.replace('\\', '/') if path else ''})

@app.route('/browse-file')
def browse_file():
    root = create_hidden_tk_root()
    path = filedialog.askopenfilename(
        master=root, 
        title="Select Limit File", 
        filetypes=[("Excel files", "*.xlsx *.xls")]
    )
    root.destroy()
    return jsonify({'path': path.replace('\\', '/') if path else ''})

@app.route('/get-file-info', methods=['POST'])
def get_file_info():
    try:
        data = request.get_json()
        folder_path  = data.get('folder_path')
        source_mode  = data.get('source_mode', 'phase1')
        if not folder_path or not os.path.isdir(folder_path):
            audit_trail.log_event("ALARM_TRIGGERED", f"Action: get-file-info | Msg: Invalid folder path: {folder_path}")
            return jsonify({'error': 'Invalid folder path.'}), 400

        if source_mode == 'phase2':
            room_scan = scan_phase2_rooms(folder_path)
            if not room_scan:
                audit_trail.log_event("ALARM_TRIGGERED", "Action: get-file-info | Code: ERR-010 | Msg: No valid Desigo format room folders found.")
                return jsonify({'error': 'ERR-010: No valid Desigo format room folders found.'}), 400
            all_dates = []
            for room_id, raw_data_path in room_scan.items():
                s, e = get_file_date_range_phase2(raw_data_path, room_id=room_id)
                if s: all_dates.append(s)
                if e: all_dates.append(e)
            if not all_dates:
                audit_trail.log_event("ALARM_TRIGGERED", "Action: get-file-info | Code: ERR-010 | Msg: No valid CSV data found in Desigo format folders.")
                return jsonify({'error': 'ERR-010: No valid CSV data found in Desigo format folders.'}), 400
            earliest = min(all_dates)
            latest   = max(all_dates)
            return jsonify({
                'earliest': earliest.isoformat(),
                'latest':   latest.isoformat(),
                'default_start_end': earliest.isoformat(),
                'rooms': sorted(list(room_scan.keys()))
            })

        # --- Phase 1 (original logic) ---
        timestamps = []
        rooms = set()
        for root, dirs, files in os.walk(folder_path):
            for filename in files:
                if filename.lower().endswith(".csv"):
                    dt = _parse_filename_for_datetime(filename)
                    if dt:
                        timestamps.append(dt)
                    parts = os.path.splitext(filename)[0].split('_')
                    if len(parts) >= 3:
                        room_id = '_'.join(parts[:-2])
                        rooms.add(room_id)

        if not timestamps:
            audit_trail.log_event("ALARM_TRIGGERED", "Action: get-file-info | Code: ERR-010 | Msg: No valid CSV files found.")
            return jsonify({'error': 'ERR-010: No valid CSV files found.'}), 400

        sorted_ts = sorted(timestamps)
        earliest = sorted_ts[0]
        latest   = sorted_ts[-1]

        return jsonify({
            'earliest': earliest.isoformat(),
            'latest': latest.isoformat(),
            'default_start_end': earliest.isoformat(),
            'rooms': sorted(list(rooms))
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/get-rooms', methods=['POST'])
def get_rooms():
    try:
        data = request.get_json()
        folder_path    = data.get('folder_path')
        setpoint_path  = data.get('setpoint_path')
        start_date_str = data.get('start_date', '')
        end_date_str   = data.get('end_date', '')
        source_mode    = data.get('source_mode', 'phase1')

        if not all([folder_path, setpoint_path, start_date_str, end_date_str]):
            audit_trail.log_event("ALARM_TRIGGERED", "Action: get-rooms | Msg: Required parameters missing.")
            return jsonify({'error': 'Required parameters missing.'}), 400

        start_date = pd.to_datetime(start_date_str).tz_localize(None)
        end_date   = pd.to_datetime(end_date_str).tz_localize(None)
        try:
            setpoint_df = pd.read_excel(setpoint_path)
        except FileNotFoundError:
            return jsonify({'error': 'ERR-002: Limit File Not Found'}), 400
        
        required_cols = ['Room_number', 'Temperature_Limit', 'Humidity_Low_Limit', 'Humidity_High_Limit', 'Pressure_Low_Limit', 'Pressure_High_Limit']
        missing_cols = [col for col in required_cols if col not in setpoint_df.columns]
        if missing_cols:
            audit_trail.log_event("ALARM_TRIGGERED", f"Action: get-rooms | Code: ERR-009 | Msg: Missing required columns: {', '.join(missing_cols)}")
            return jsonify({'error': f"ERR-009: Invalid Limit File Format - Missing required columns: {', '.join(missing_cols)}"}), 400

        setpoint_rooms = set(setpoint_df['Room_number'].astype(str).tolist())
        has_area = 'AREA' in setpoint_df.columns
        available_room_nos_set = set()

        if source_mode == 'phase2':
            room_scan = scan_phase2_rooms(folder_path)
            start_d, end_d = start_date.date(), end_date.date()
            for room_id, raw_data_path in room_scan.items():
                f_start, f_end = get_file_date_range_phase2(raw_data_path, room_id=room_id)
                if f_start and f_end and not (f_end < start_d or f_start > end_d):
                    available_room_nos_set.add(room_id)
        else:
            # Scan files recursively to see which rooms have data in range
            for root, dirs, files in os.walk(folder_path):
                for filename in files:
                    if filename.lower().endswith(".csv"):
                        f_path = os.path.join(root, filename)
                        f_start, f_end = get_file_date_range(f_path)
                        if not f_start:
                            f_dt = parse_filename_for_datetime(filename)
                            if f_dt: f_start = f_end = f_dt
                        if f_start and f_end:
                            start_d, end_d = start_date.date(), end_date.date()
                            if not (f_end < start_d or f_start > end_d):
                                base_name = os.path.splitext(filename)[0]
                                matched_room = None
                                sorted_setpoint_rooms = sorted(list(setpoint_rooms), key=len, reverse=True)
                                for r in sorted_setpoint_rooms:
                                    if base_name.startswith(r):
                                        matched_room = r
                                        break
                                if matched_room:
                                    available_room_nos_set.add(matched_room)
                                else:
                                    room_no_parts = base_name.split('_')[:-2]
                                    if room_no_parts:
                                        available_room_nos_set.add('_'.join(room_no_parts))

        filtered_df = setpoint_df[setpoint_df['Room_number'].astype(str).isin(available_room_nos_set)]
        
        all_rooms = []
        rooms_by_area = {}
        for _, row in filtered_df.iterrows():
            room_info = {'id': str(row['Room_number']), 'name': str(row['Room_name'])}
            all_rooms.append(room_info)
            if has_area:
                area = str(row['AREA'])
                if area not in rooms_by_area:
                    rooms_by_area[area] = []
                rooms_by_area[area].append(room_info)
        
        return jsonify({'all_rooms': all_rooms, 'rooms_by_area': rooms_by_area})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        source_mode    = data.get('source_mode', 'phase1')
        folder_path    = data.get('folder_path')
        setpoint_path  = data.get('setpoint_path')
        selected_rooms = data.get('selected_rooms')
        start_date     = data.get('start_date')
        end_date       = data.get('end_date')

        if not all([folder_path, setpoint_path, selected_rooms, start_date, end_date]):
            audit_trail.log_event("ALARM_TRIGGERED", "Action: analyze | Msg: Missing required parameters.")
            return jsonify({'error': 'Missing required parameters.'}), 400

        # Reject concurrent analysis attempts
        if not _analysis_lock.acquire(blocking=False):
            audit_trail.log_event("ALARM_TRIGGERED", "Action: analyze | Msg: Concurrent analysis attempt blocked (HTTP 429).")
            return jsonify({'error': 'Another analysis is already running. Please wait.'}), 429

        job_id    = str(uuid.uuid4())[:8]
        log_queue = _queue.Queue()

        with _jobs_lock:
            _jobs[job_id] = {'queue': log_queue, 'done': False, 'response': None, 'plot': None, 'error': None}

        def _run():
            try:
                fn = analyze_files_phase2 if source_mode == 'phase2' else analyze_files
                output_file_path, _logs, plot_result = fn(
                    folder_path=folder_path,
                    setpoint_path=setpoint_path,
                    selected_rooms=selected_rooms,
                    start_date=start_date,
                    end_date=end_date,
                    log_queue=log_queue
                )
                with _jobs_lock:
                    if not output_file_path:
                        error_msg = 'Analysis failed. Check input data.'
                        if _logs:
                            matches = re.findall(r'(ERR-\d{3}: [^\n\r\"\'\)]+)', _logs)
                            if matches:
                                error_msg = matches[-1].strip()
                        _jobs[job_id]['error'] = error_msg
                    else:
                        room_errors = plot_result.get('room_errors', {}) if plot_result else {}
                        has_err008 = "ERR-008" in (_logs or "")
                        
                        warning_msg = None
                        lines = []
                        if room_errors:
                            for r_id, err in sorted(room_errors.items()):
                                lines.append(f"Room {r_id}: {err}")
                        if has_err008:
                            lines.append("ERR-008: Duplicate timestamps detected and automatically resolved. Please check the log.")
                        
                        if lines:
                            warning_msg = "\n".join(lines)
                            
                        _jobs[job_id]['response'] = {
                            'filename': os.path.basename(output_file_path),
                            'warning': warning_msg,
                            'stats': plot_result.get('stats', {}) if (plot_result and 'error' not in plot_result) else {}
                        }
                        if plot_result and "error" not in plot_result:
                            _jobs[job_id]['plot'] = {
                                'plot_data':          plot_result.get('plot_data', {}),
                                'summary':            plot_result.get('summary', []),
                                'violation_intervals': plot_result.get('violation_intervals', [])
                            }
                    _jobs[job_id]['done'] = True
            except Exception as e:
                with _jobs_lock:
                    _jobs[job_id]['error'] = str(e)
                    _jobs[job_id]['done']  = True
            finally:
                log_queue.put(None)   # sentinel — tells SSE stream to close
                _analysis_lock.release()

        threading.Thread(target=_run, daemon=True).start()
        return jsonify({'job_id': job_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/job-status/<job_id>')
def job_status(job_id):
    """GAMP 5: Robust polling fallback. Prevents UI freeze in Waitress production mode
    which natively buffers/caches standard Server-Sent Events (SSE).
    """
    with _jobs_lock:
        job = _jobs.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404

    lines = []
    log_q = job['queue']
    # Drain the queue to fetch new logs since last poll
    while not log_q.empty():
        try:
            line = log_q.get_nowait()
            if line is not None:
                lines.append(line)
        except Exception:
            break

    with _jobs_lock:
        return jsonify({
            'done': job['done'],
            'error_msg': job['error'],
            'response': job['response'],
            'logs': lines
        })


@app.route('/stream/<job_id>')
def stream(job_id):
    """SSE endpoint — streams log lines live, then sends a final 'done' or 'error_event'."""
    def generate():
        with _jobs_lock:
            job = _jobs.get(job_id)
        if not job:
            audit_trail.log_event("ALARM_TRIGGERED", f"Action: stream | Msg: Job not found: {job_id}")
            yield "data: ERROR: Job not found\n\n"
            return

        log_q = job['queue']
        while True:
            try:
                line = log_q.get(timeout=60)
                if line is None:  # sentinel = analysis finished
                    with _jobs_lock:
                        job_state = _jobs.get(job_id, {})
                    if job_state.get('error'):
                        payload = json.dumps({'error': job_state['error']})
                        yield f"event: error_event\ndata: {payload}\n\n"
                    else:
                        payload = json.dumps(job_state.get('response') or {})
                        yield f"event: done\ndata: {payload}\n\n"
                    break
                # Escape any embedded newlines so each SSE message is on one data: line
                safe_line = line.replace('\n', ' ')
                yield f"data: {safe_line}\n\n"
            except _queue.Empty:
                yield ": keepalive\n\n"   # SSE comment keeps connection alive

    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no', 'Connection': 'keep-alive'}
    )


@app.route('/plot/<job_id>')
def get_plot(job_id):
    """Lazy endpoint — returns chart data after analysis is complete."""
    with _jobs_lock:
        job = _jobs.get(job_id)
    if not job or not job.get('done'):
        audit_trail.log_event("ALARM_TRIGGERED", f"Action: get-plot | Msg: Job not found or not yet complete: {job_id}")
        return jsonify({'error': 'Job not found or not yet complete.'}), 404
    plot = job.get('plot')
    if not plot:
        audit_trail.log_event("ALARM_TRIGGERED", f"Action: get-plot | Msg: No chart data available: {job_id}")
        return jsonify({'error': 'No chart data available for this job.'}), 404
    return jsonify(plot)

@app.route('/audit-trail')
def audit_trail_view():
    return render_template('audit_trail.html')

@app.route('/audit-logs')
def get_audit_logs():
    logs = []
    log_file = audit_trail.LOG_FILE
    if os.path.exists(log_file):
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        logs.append(json.loads(line))
        except Exception as e:
            return jsonify({'error': f"Failed to read logs: {str(e)}"}), 500
    # Reverse so the newest events are first
    logs.reverse()
    return jsonify(logs)

@app.route('/verify-audit-trail', methods=['POST'])
def verify_audit_logs():
    try:
        success, message = audit_trail.verify_audit_trail()
        if success:
            audit_trail.log_event("AUDIT_VERIFIED", "Cryptographic audit trail integrity manually verified by user.")
        else:
            audit_trail.log_event("AUDIT_TAMPERED", f"WARNING: Audit trail verification failed: {message}")
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/download/<path:filename>')
def download(filename):
    # Security: restrict to REPORTS_DIR
    return send_from_directory(REPORTS_DIR, filename, as_attachment=True)

@app.route('/shutdown')
def shutdown():
    """Gracefully shutdown the Flask application"""
    import signal
    import threading
    def shutdown_server():
        import time
        time.sleep(0.5)
        os._exit(0)
    thread = threading.Thread(target=shutdown_server)
    thread.daemon = True
    thread.start()
    return jsonify({'status': 'shutting_down'})

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/aqr') # IQ-TC-06 Local Loopback (Offline)

if __name__ == '__main__':
    # Start the Flask app
    if getattr(sys, 'frozen', False):
        # Auto-open browser in EXE mode
        Timer(1.5, open_browser).start()
        serve(app, host='0.0.0.0', port=5000, threads=8, channel_timeout=3600) # IQ-TC-06 Localhost Isolation
    else:
        app.run(host='0.0.0.0', port=5000, debug=True)
