# CODEBASE GRAPH: AirQualityReview_Project

## 1. Core Architecture
- **Tech Stack**: Python, Flask, Pandas, Plotly, Waitress (WSGI), PyInstaller.
- **Pattern**: 
  - **Backend**: Flask API handling data processing and report generation.
  - **Frontend**: HTML/JS/CSS templates communicating with Flask via REST APIs.
  - **Data Processing**: Heavy Pandas usage for CSV transformation, merging, and condition checking against limits.
  - **Desktop Integration**: Uses `tkinter` for native file dialogs and `webbrowser` to auto-launch the UI. Packs into a standalone `.exe`.

## 2. Main Entry Points
- `app.py`: The Flask server entry point.
  - Initializes `audit_trail` to ensure GAMP 5 compliance on startup.
  - Exposes REST endpoints (`/api/transform/split-reports`, `/analyze`, `/get-plot-data`). Handles splitting of Main Plant, Module 5, and Pilot Plant CSV formats.
  - Uses `Waitress` for production-grade local serving when built as an executable.

## 3. Key Modules & Graph
- **`analysis_logic.py`** (The Brain)
  - `prepare_df()`: Cleans and formats raw BAS CSV data into standardized Pandas DataFrames.
  - `analyze_files()`: Core loop. Compares room Temperature/Humidity/Pressure against limits (`SetPointLimit.xlsx`).
  - `check_reverse_violations()`: Complex logic for corridor vs. room pressure hierarchies.
  - `get_plot_info()`: Outputs JSON-friendly data for Plotly charting on the frontend.
- **`audit_trail.py`** (GAMP 5 Security)
  - Ensures logs cannot be tampered with. System halts (`FATAL ERROR 004`) if corrupted.
- **`app.spec`** & **`BUILD_INSTRUCTIONS.md`** (Deployment)
  - Configuration for PyInstaller to bundle Flask templates/static files into a single `.exe`.

## 4. Constraints & Technical Risks
- **GAMP 5 Compliance**: Strict requirements for Audit Trails, data integrity (SHA256 hashing), and error handling.
- **AI Module Removed**: The project previously used `google-genai` for report review, but it has been explicitly removed (`agent_module.py` deleted, `requirements.txt` commented out).
- **Time/Date Parsing**: Fragile dependency on specific BAS filename formats (e.g., `[ROOM]_[MM-DD-YY]_[HH-MM].csv`).
- **Pressure Corridor Logic**: Interdependent room pressure comparisons require exact room configurations in the SetPoint Excel sheet.
