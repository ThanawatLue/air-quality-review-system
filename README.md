# Air Quality Review (AQR) System

> **Validated Data Analytics for Industrial Compliance**
> *Built with GAMP 5 standards in mind for high-integrity environmental monitoring and reporting.*

---

## 🛡️ Compliance & Quality Highlights
- **GAMP 5 Aligned:** Developed following GAMP 5 (Good Automated Manufacturing Practice) software category 4 guidelines.
- **Data Integrity:** Implements strict data validation, temporal alignment (using `merge_asof`), and error-handling protocols (ERR-001 through ERR-006).
- **Audit-Ready Reporting:** Generates standardized, immutable reports for environmental review with integrated audit trail logic.
- **Enterprise Ready:** Optimized for BAS (Building Automation System) data ingestion with room-level segmentation and setpoint limit verification.

---

## Project Structure

```
AirQualityReview_Project/
├── app.py                 # Main Flask application
├── analysis_logic.py      # Data analysis logic
├── app.spec              # PyInstaller build configuration
├── requirements.txt      # Python dependencies
├── templates/            # HTML templates
│   ├── aqr.html
│   ├── transform.html
│   └── index.html
├── static/               # CSS and JavaScript
│   ├── style.css
│   └── script.js
└── data/                 # Sample data files
    ├── SetPointLimit.xlsx
    └── CSV files...
```

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application (development mode):**
   ```bash
   python app.py
   ```
   
   The application will open in your browser at `http://127.0.0.1:5000/aqr`

## Building Executable (.exe)

### Using PyInstaller

1. **Install PyInstaller** (if not already installed):
   ```bash
   pip install pyinstaller
   ```

2. **Build the executable:**
   ```bash
   pyinstaller app.spec
   ```
   
   Or using command line:
   ```bash
   pyinstaller --onefile --windowed --add-data "templates;templates" --add-data "static;static" --add-data "data;data" app.py
   ```

3. **Find the executable:**
   - The `.exe` file will be in the `dist/` folder
   - Filename: `app.exe` (or as specified in app.spec)

### Build Options Explained

- `--onefile`: Creates a single executable file
- `--windowed`: Runs without console window (GUI mode)
- `--add-data`: Includes data folders (templates, static, data)
- `app.spec`: Configuration file for PyInstaller

## Running the Executable

### For End Users

1. **Install Microsoft Visual C++ Redistributable** (Required):
   - Download from: https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170
   - Install the x64 version

2. **Prepare folders:**
   - Create a `reports` folder in the same directory as the `.exe` file
   - This folder is required for output reports

3. **Run the application:**
   - Double-click the `.exe` file
   - The application will open in your default browser

## Application Features

### Air Quality Review (AQR)
- Analyze CSV data from BAS systems
- Compare against setpoint limits
- Generate Excel reports

### Data Transformation
- Split reports by room
- Process Module 5 and Main Plant data
- Custom CSV formatting

### AI Review (Module Removed)
- AI-powered periodic review module has been removed from this version

## Data Requirements

### Input Files
- **CSV Files**: BAS data in format `[ROOM]_[MM-DD-YY]_[HH-MM].csv`
- **Limit File**: Excel file with setpoint limits (SetPointLimit.xlsx)

### Output
- Reports generated in `reports/` folder
- Excel format (.xlsx)

## Troubleshooting

### Common Issues

**Error: Failed to load Python DLL**
- Solution: Install Microsoft Visual C++ Redistributable

**Error: Module not found**
- Solution: Ensure all dependencies are installed via `pip install -r requirements.txt`

**Application won't start**
- Check that `reports` folder exists
- Verify data files are in correct locations
- Check browser console for errors

## Development

### Running in Debug Mode
```bash
python app.py
```

### Testing
- Access the application at `http://127.0.0.1:5000/aqr`
- Debug mode is enabled by default in development

## License

Proprietary - Air Quality Review Application

## Support

For issues or questions, please contact the development team.
