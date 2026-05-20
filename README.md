# Air Quality Review (AQR) System

> **Validated Data Analytics for Industrial Compliance**
> *Built with GAMP 5 standards in mind for high-integrity environmental monitoring and reporting.*

**Current Version: 1.1.0**

---

## Compliance & Quality Highlights

- **GAMP 5 Aligned:** Developed following GAMP 5 (Good Automated Manufacturing Practice) software category 4 guidelines.
- **Data Integrity:** Implements strict data validation, temporal alignment (using `merge_asof`), and error-handling protocols (ERR-001 through ERR-007).
- **Audit-Ready Reporting:** Generates standardized, immutable Excel reports with integrated audit trail logging.
- **Enterprise Ready:** Supports both BAS (Phase I) and EMS (Phase II) data sources with room-level segmentation and setpoint limit verification.
- **Scalable Streaming:** Real-time log streaming via Server-Sent Events (SSE) — designed to handle thousands of rooms without browser freezing.

---

## Project Structure

```
AirQualityReview_Project/
├── app.py                        # Main Flask application + all API routes
├── analysis_logic.py             # Core data analysis engine (Phase I & II)
├── audit_trail.py                # GAMP 5 audit trail module
├── app.spec                      # PyInstaller build configuration
├── app_version_info.txt          # Windows version metadata for .exe
├── requirements.txt              # Python dependencies
├── templates/
│   ├── aqr.html                  # Air Quality Review page
│   ├── transform.html            # Data Transformation page
│   └── index.html                # Root redirect
├── static/
│   ├── style.css                 # Application stylesheet
│   └── script.js                 # Frontend logic (SSE, charts, room selection)
├── data/
│   ├── SetPointLimit.xlsx        # Phase I setpoint limits (~150 rooms)
│   ├── SetPointLimit_Phase2.xlsx # Phase II setpoint limits (221 rooms)
│   └── C/                        # Sample Phase I CSV data files
├── reports/                      # Generated Excel reports (auto-created)
├── logs/                         # Audit trail logs (auto-created)
└── validation_docs/              # GAMP 5 validation documentation
```

---

## Architecture Overview

### Real-Time Streaming (SSE + Background Thread)

The analysis pipeline uses a non-blocking architecture to support large datasets (hundreds to tens of thousands of rooms) without freezing the browser:

```
Browser                                 Flask Server
  │                                         │
  ├─ POST /analyze ──────────────────────► │ Validate inputs
  │                                         │ Acquire analysis lock
  │ ◄── { job_id: "abc123" } ─────────────┤ Spawn background thread
  │                                         │ Return immediately
  │                                         │
  ├─ GET /stream/abc123 (SSE) ───────────► │ Open SSE connection
  │ ◄═ "Processing Room: 1-P038..." ══════╡ Stream log lines live
  │ ◄═ "Temperature Violations..." ═══════╡ as each room finishes
  │ ◄═ "Completed Room: 1-P038" ══════════╡
  │ ◄═ event:done { filename, warning } ══╡ Analysis complete
  │                                         │
  ├─ GET /plot/abc123 ────────────────────► │ Fetch chart data (lazy)
  │ ◄── { plot_data, summary, intervals } ─┤ Only when user requests graphs
```

**Key benefits:**
- Browser never waits for analysis to complete — log streams in real-time
- `/analyze` returns in < 1ms regardless of dataset size
- Chart data (`plot_data`) is fetched lazily — only when user clicks "Generate Visual Graphs"
- Only one analysis can run at a time (protected by `_analysis_lock`)

### Log Rendering (requestAnimationFrame Batching)

All SSE log lines are buffered in JavaScript and flushed to the DOM via `requestAnimationFrame`, capping DOM updates at 60/sec regardless of how fast lines arrive. This prevents O(n²) `innerText +=` freezing that would occur with naive per-event DOM updates.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/aqr` | Main AQR dashboard |
| `GET` | `/transform` | Data Transformation module |
| `POST` | `/analyze` | Start analysis job → returns `{ job_id }` immediately |
| `GET` | `/stream/<job_id>` | SSE stream — log lines + final `done`/`error_event` |
| `GET` | `/plot/<job_id>` | Lazy fetch of chart data after analysis completes |
| `POST` | `/get-file-info` | Scan folder and return date range |
| `POST` | `/get-rooms` | Return rooms available in the selected date range |
| `GET` | `/download/<filename>` | Download generated Excel report |
| `GET` | `/browse-folder` | Open OS folder picker dialog |
| `GET` | `/browse-file` | Open OS file picker dialog |
| `GET` | `/shutdown` | Gracefully shut down the application |

---

## Application Modules

### 1. Air Quality Review (AQR)

**Workflow:**
1. **Step 1 — Configuration:** Select Phase I or Phase II mode, choose data folder and setpoint limit file.
2. **Step 2 — Analysis Period:** Set start/end date-time (auto-populated from file metadata).
3. **Step 3 — Room Selection:** Filter by area, select individual or all rooms.
4. **Generate Summary Reports:** Runs analysis in background; live log streams to the terminal panel.
5. **Generate Visual Graphs:** Lazily fetches chart data and renders all visualizations.

**Generate Summary Reports button** triggers background analysis. Log output streams in real-time to the "AQR Program Detailed Analysis Log" panel. The "Generate Visual Graphs" button is greyed out and disabled until a successful analysis has been completed.

**Violation Detection Logic (25-Minute Rule):**
- A violation is only flagged if the parameter exceeds the limit for 25 continuous minutes or more.
- Implemented via: `datetime.diff(5).dt.total_seconds() == 1500` — ensures exactly 6 consecutive 5-minute readings with no gaps.

**Violation Log Detail:**
- Each violation block prints the full violation DataFrame with no row limit.
- Header lines include the applicable limit value, e.g.: `Temperature Violations Found for 1-P038: (Limit: ≤ 25.0 °C)`

**Analysis Results Categories:**
- `Passed` — No qualifying violations
- `Out of spec` — Violations ≥ 25 minutes
- `Data Loss` — NaN values found in sensor column
- `Out of spec & Data Loss` — Both conditions
- `N/A` — No setpoint defined for that parameter

### 2. Data Transformation

Splits consolidated BAS report files into per-room CSV files in the standard format required for Phase I analysis.

- Supports Main Plant (RMT/RMH/RPT files)
- Supports Module 5
- Supports Pilot Plant
- Outputs per-room CSV files with correct header format

---

## Phase I vs Phase II

| Item | Phase I (BAS) | Phase II (EMS) |
|------|--------------|----------------|
| File structure | Flat — one file per room per day | Folder tree: `AHU / Room / Raw Data /` |
| T / H / P data | Combined in one file (Point_1/2/3) | Three separate files (_RMT_, _RMH_, _RDP_) |
| Delimiter | Comma `,` | Semicolon `;` |
| Header rows | Multi-row with point mapping | 4 fixed rows |
| Numeric format | Decimal | Scientific notation (`2.137E+1`) |
| Date format | MM/DD/YYYY | DD/MM/YYYY (`dayfirst=True`) |
| Room ID | In filename (e.g. `1-P038`) | File prefix (e.g. `10-1-096`) |
| Rooms | ~150 | 221 |
| Setpoint file | `SetPointLimit.xlsx` | `SetPointLimit_Phase2.xlsx` |
| Report filename | `AQR_Report_YYYYMMDD_HHMMSS.xlsx` | `AQR_Report_P2_YYYYMMDD_HHMMSS.xlsx` |

### Phase II File Structure

```
[root_folder]/
├── [AHU_name]/                          e.g. 101-AHU01
│   ├── [Room_name]/                     e.g. RM096
│   │   └── Raw Data/                   (or any subfolder — scanned recursively)
│   │       ├── 10-1-096_RMT_YYYY-MM-DD_HH-MM-SS_1.Csv   ← Temperature
│   │       ├── 10-1-096_RMH_YYYY-MM-DD_HH-MM-SS_1.Csv   ← Humidity
│   │       └── 10-1-096_RDP_YYYY-MM-DD_HH-MM-SS_1.Csv   ← Pressure (optional)
│   └── ...
└── ...
```

**Notes:**
- Multiple files per type per room are supported (concatenated automatically).
- Rooms with no RMH file and a humidity setpoint → `Humidity: Data Loss`.
- Rooms with no RMH file and **no** humidity setpoint (blank in Excel) → `Humidity: N/A`.
- Rooms with no RDP file and a pressure setpoint → `Pressure: Data Loss`.
- Footer rows in files (e.g. "Acceptance Criteria") are filtered out automatically via `errors='coerce'`.

---

## Setpoint File Format

Both phases use the same Excel column layout:

| Column | Description | Phase I example | Phase II example |
|--------|-------------|----------------|-----------------|
| `Room_number` | Unique room ID | `1-P038` | `10-1-096` |
| `Room_name` | Display name | `Dispensing Room A` | `RM096` |
| `AREA` | Area/group label | `Module 1` | `101-AHU01` |
| `Temperature_Limit` | Max temp (°C) | `25` | `25` |
| `Humidity_Low_Limit` | Min humidity (%RH) | `30` | `35` |
| `Humidity_High_Limit` | Max humidity (%RH) | `60` | `65` |
| `Pressure_Low_Limit` | Min pressure (Pa) | `10` | `25` |
| `Pressure_High_Limit` | Max pressure (Pa) | `20` | `35` |
| `Room_Pressure_Comparison` | Corridor room ID for pressure comparison | `1-C001` | _(optional)_ |

**Rules for blank/NaN cells:**
- `Temperature_Limit` blank → limit treated as 100°C (effectively no limit)
- `Humidity_Low_Limit` **and** `Humidity_High_Limit` both blank → `Humidity: N/A` (no humidity monitoring)
- `Pressure_Low_Limit` **or** `Pressure_High_Limit` blank → `Pressure: N/A` (no pressure monitoring)

---

## Error Codes

| Code | Name | Description |
|------|------|-------------|
| `ERR-001` | Header Missing | CSV file does not contain the `<>Date` header row |
| `ERR-002` | Limit File Not Found | The specified setpoint Excel file does not exist |
| `ERR-003` | Invalid Configuration | Limit values in setpoint file are non-numeric |
| `ERR-004` | Audit Trail Corrupt | Audit trail integrity check failed on startup — system halts |
| `ERR-005` | Invalid File Format | Required columns (Temperature, Humidity) not found in CSV |
| `ERR-006` | Logical Constraint | High limit is lower than low limit in setpoint file |
| `ERR-007` | Report Generation Failed | Excel export failed (disk full, permissions, etc.) |

---

## Visual Graphs

Clicking **Generate Visual Graphs** (available only after a successful analysis) fetches chart data from `/plot/<job_id>` and renders:

| Chart | Description |
|-------|-------------|
| **Violation Intensity Heatmap** | Day × Hour grid showing concurrent violation density |
| **Violation Timeline** | Gantt-style chart of all violation intervals per room (> 25 min) |
| **Violation Overview** | Stacked bar chart — violation count per room (T / H / P) |
| **Statistical Violation Table** | Clickable table to isolate individual rooms in detail plots |
| **Temperature Monitor** | Time-series line chart for all selected rooms |
| **Humidity Monitor** | Time-series line chart with adjustable H/L limit lines |
| **Pressure Monitor** | Time-series line chart with adjustable H/L limit lines |

**Interactive features:**
- All time-series charts are X-axis synchronized — panning one pans all.
- Clicking a room in the summary chart or timeline isolates it in the detail plots.
- Limit lines on detail plots are draggable (updates the input fields).
- Range selector buttons: 1H / 1D / 7D / 30D / ALL.

---

## Installation

### Prerequisites

- Python 3.7 or higher
- pip

### Setup

```bash
pip install -r requirements.txt
python app.py
```

The application opens automatically at `http://127.0.0.1:5000/aqr`

> In development mode (`python app.py`), Flask's built-in server is used with `debug=True`. SSE streaming works natively.

---

## Building Executable (.exe)

See [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) for full step-by-step instructions.

**Quick build:**
```bash
pip install pyinstaller
pyinstaller app.spec
```

The `.exe` will be in `dist/`. Copy it alongside an empty `reports/` folder before distributing.

**Production server:** The `.exe` uses Waitress WSGI server (`threads=8`, `channel_timeout=3600`) for SSE-compatible streaming without needing a separate reverse proxy.

---

## Data Requirements

### Phase I — Input CSV Format (BAS)

**Filename:** `[ROOM_ID]_[MM-DD-YY]_[HH-MM].csv`

Example: `1-P038_05-12-25_01-00.csv`

> Note: The date in the filename is the *export* date. The system automatically subtracts 1 day to get the *data* date (business logic for BAS reports).

**CSV structure:**
```
"Key  Name:Suffix  Trend Definitions Used"
"Point_1:","1-P038 ROOM TEMP","","5 minutes"
"Point_2:","1-P038 ROOM HUM","","5 minutes"
"Point_3:","1-P038 ROOM PRES","","5 minutes"
"Time Interval:","5 Minutes"
...
"<>Date","Time","Point_1","Point_2","Point_3"
"05/12/2025","00:00","22.1","45.2","15.3"
...
```

### Phase II — Input CSV Format (EMS)

**Filename:** `[ROOM_ID]_RMT_[YYYY-MM-DD]_[HH-MM-SS]_1.Csv` (and `_RMH_`, `_RDP_` variants)

**CSV structure (semicolon-delimited, 4 header rows):**
```
row1: metadata
row2: metadata
row3: metadata
row4: column headers
DD/MM/YYYY HH:MM:SS ; Source ; Value
01/05/2026 00:00:00 ; ... ; 2.137E+1
```

### Output

- Excel report (`.xlsx`) saved to `reports/` folder
- Filename: `AQR_Report_YYYYMMDD_HHMMSS.xlsx` (Phase I) or `AQR_Report_P2_YYYYMMDD_HHMMSS.xlsx` (Phase II)
- Report contains: period header, date separator rows, per-room specification and analysis results

---

## Key Source Files

### `analysis_logic.py`

| Function / Class | Description |
|-----------------|-------------|
| `QueueWriter` | Drop-in replacement for `io.StringIO` — captures `print()` output and streams each line into a `queue.Queue` for SSE delivery while also buffering the full log |
| `analyze_files(...)` | Phase I analysis pipeline — accepts optional `log_queue` for SSE streaming |
| `analyze_files_phase2(...)` | Phase II analysis pipeline — same interface as Phase I |
| `_compute_plot_result(...)` | Shared function — builds `plot_data`, `summary`, `violation_intervals` from pre-loaded DataFrames |
| `prepare_df(file_path)` | Parse a Phase I CSV into a DataFrame with DateTime/Temperature/Humidity/Pressure columns |
| `prepare_df_phase2(raw_data_path)` | Parse Phase II RMT/RMH/RDP files → returns `(room_id, df, sensors)` |
| `scan_phase2_rooms(folder_path)` | Recursively find all Phase II rooms → `{room_id: dir_path}` |
| `_print_df(df)` | Print a DataFrame to stdout with no row limit |
| `find_continuous_ranges(lst)` | Find consecutive index ranges (used for 25-minute rule) |
| `check_reverse_violations(...)` | Verify corridor pressure relationships for dependent rooms |

### `app.py`

| Component | Description |
|-----------|-------------|
| `_jobs` dict | In-memory job store: `{ job_id: { queue, done, response, plot, error } }` |
| `_analysis_lock` | `threading.Lock` — prevents concurrent analyses (stdout redirect safety) |
| `_jobs_lock` | `threading.Lock` — protects `_jobs` dict from race conditions |
| `/analyze` route | Acquires lock, spawns background thread, returns `job_id` immediately |
| `/stream/<job_id>` | SSE generator — reads queue line by line, sends `event: done` or `event: error_event` when finished |
| `/plot/<job_id>` | Returns stored `plot_data`, `summary`, `violation_intervals` after analysis completes |

### `static/script.js`

| Variable / Function | Description |
|--------------------|-------------|
| `currentSourceMode` | `'phase1'` or `'phase2'` — sent with every API call |
| `currentJobId` | Job ID of the most recent successful analysis — used by `/plot/<job_id>` |
| `lastAnalysisPlotResult` | Cached chart data — prevents re-fetching when re-clicking Generate Visual Graphs |
| `setPlotBtnEnabled(bool)` | Enables/disables the Generate Visual Graphs button |
| `_flushLog()` | `requestAnimationFrame` loop — batches SSE log lines into DOM text nodes at ≤60 fps |
| `renderPlots(plotData)` | Renders Temperature, Humidity, Pressure time-series charts with synchronized x-axis |
| `renderTimelineChart(intervals)` | Renders Gantt-style violation timeline |
| `renderHeatmap(intervals)` | Renders Day × Hour violation heatmap |
| `isolateRoomInDetailPlots(roomId)` | Highlights one room across all detail charts |

---

## Troubleshooting

### Application won't start
- Ensure `reports/` folder exists in the same directory as the `.exe`
- Check that port 5000 is not in use by another process
- Install Microsoft Visual C++ Redistributable (x64) if running the `.exe`

### "Another analysis is already running"
- HTTP 429 is returned if a second Analyze is triggered while one is in progress
- Wait for the current analysis to finish before starting another

### Log terminal shows nothing / stops mid-stream
- Check browser console for SSE connection errors
- Ensure the server is still running (check the console window or task manager)
- The SSE connection has a 60-second idle timeout — if no log lines are produced for 60s, a keepalive comment is sent to maintain the connection

### Excel report not downloading
- Verify the `reports/` folder exists and is writable
- Check for ERR-007 in the log — this indicates an Excel write failure

### Phase II rooms not appearing in room list
- Confirm the folder structure contains `_RMT_` files at some depth
- `scan_phase2_rooms()` requires at least one `_RMT_` file to register a room
- Verify the room ID in the filename prefix matches `SetPointLimit_Phase2.xlsx`

### Graphs not rendering after analysis
- The "Generate Visual Graphs" button is disabled until a successful analysis completes
- If the button is enabled but graphs are blank, check browser console for JSON parse errors
- The `/plot/<job_id>` endpoint returns 404 if the job is not yet done or had no chart data

---

## Pressure Comparison Logic

For rooms with a `Room_Pressure_Comparison` value defined in the setpoint file, pressure violations are validated against the corridor room:

| Room type | `Pressure_Low_Limit` | Violation condition |
|-----------|----------------------|---------------------|
| High-pressure (≥ 35 Pa) | ≥ 35 | Room pressure *below* corridor = `Out of spec` |
| Standard (< 35 Pa) | < 35 | Room pressure *above* corridor = `Out of spec` |

If the room IS a corridor room (`Room_number` appears in any `Room_Pressure_Comparison` column), reverse violations are also checked: dependent rooms that should be above/below the corridor are validated simultaneously.

---

## Phase II — Remaining Work

### High Priority
- [ ] Fill in real `Room_name` values for all 221 rooms in `SetPointLimit_Phase2.xlsx`
- [ ] Verify actual T/H/P spec values per zone (may differ from defaults)
- [ ] Define `Room_Pressure_Comparison` for rooms requiring corridor comparison
- [ ] Refine AREA grouping (currently uses AHU name)

### Validation & Testing
- [ ] Full end-to-end test with real Phase II data for all 221 rooms
- [ ] Verify `dayfirst=True` date parsing is correct for all room data files
- [ ] Confirm pressure corridor comparison logic with real data
- [ ] Verify multi-file concat (multiple files per room per type)
- [ ] Validate Excel report format against Phase I output for consistency

### Build & Deploy
- [ ] Update `app.spec` if new dependencies are added
- [ ] Build and test `.exe` with Phase II data
- [ ] Bump version to v1.2.0 after Phase II validation is complete

---

## License

Proprietary — Air Quality Review Application

## Support

For issues or questions, please contact the development team.
