import re

md_path = r"C:\Users\thana\My Drive\GPO\Appendix 2_Module\Appendix 2_Enclosure 1.md"

with open(md_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace placeholders with code blocks
replacements = [
    (r'\[รูปภาพประกอบ \(ลบออกแล้ว\)\]\s*\(Figure 01: Source Code for log_event Function \(Reference: CRR-TC-01\)', 
     '''```python
def log_event(action, details=""):
    """Logs an event with a tamper-evident hash-chain."""
    # GAMP 5: Ensure log directory exists (IQ-TC-02)
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # CRR-TC-01: User Identity Capture Verification (Ref: CRR-01)
    # Use getpass.getuser() to reliably get the human/service account identity
    try:
        user = getpass.getuser()
    except Exception:
        user = os.environ.get('USERNAME', 'UNKNOWN_USER')
```\n*(Figure 01: Source Code for log_event Function (Reference: CRR-TC-01)*'''),
    
    (r'\[รูปภาพประกอบ \(ลบออกแล้ว\)\]\s*\(Figure 02: Source Code for temporal alignment with 60s \(Reference: CRR-TC-01\)',
     '''```python
        # GAMP 5: Align mismatched sensor timestamps dynamically using merge_asof with a 60s tolerance window
        comparison_df = pd.merge_asof(
            df.sort_values("DateTime"),
            corridor_df.sort_values("DateTime")[["DateTime", "Pressure"]].rename(columns={"Pressure": "Corridor_Pressure"}),
            on="DateTime",
            direction="nearest",
            tolerance=pd.Timedelta("60s")
        )
```\n*(Figure 02: Source Code for temporal alignment with 60s (Reference: CRR-TC-02)*'''),
    
    (r'\[รูปภาพประกอบ \(ลบออกแล้ว\)\]\s*\(Figure 03: Source Code for temporal alignment with 60s \(Reference: CRR-TC-01\)',
     '''*(Duplicate removed)*'''),
     
    (r'\[รูปภาพประกอบ \(ลบออกแล้ว\)\]\s*\(Figure 04: Source Code for software version identify \(Reference: IQ-TC-01\)',
     '''```python
                # GAMP 5: UR-FN-08 Hardcode version and generation date (IQ-TC-01)
                ws.write(0, last_col, f'Software Version: v1.1.0\\nGenerated: {time.strftime("%Y-%m-%d %H:%M")}', fmt_center)
```\n*(Figure 04: Source Code for software version identify (Reference: IQ-TC-01)*'''),
     
    (r'\[รูปภาพประกอบ \(ลบออกแล้ว\)\]\s*\(Figure 05: Source Code for software version identify \(Reference: IQ-TC-01\)',
     '''*(Duplicate removed)*'''),
     
    (r'\[รูปภาพประกอบ \(ลบออกแล้ว\)\]\s*\(Figure 06: Source Code for automatically creating folders and the core security log file \(Reference: IQ-TC-02 and IQ-TC-04\)',
     '''```python
# GAMP 5: Reports directory setup
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')
if not os.path.exists(REPORTS_DIR):
    os.makedirs(REPORTS_DIR)

# GAMP 5: Logs directory setup (UR-DI-01, IQ-TC-02, IQ-TC-04)
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)
```\n*(Figure 06: Source Code for automatically creating folders and the core security log file (Reference: IQ-TC-02 and IQ-TC-04)*'''),
     
    (r'\[รูปภาพประกอบ \(ลบออกแล้ว\)\]\s*\(Figure 07: Source Code for automatically creating folders and the core security log file \(Reference: IQ-TC-02 and IQ-TC-04\)',
     '''*(Duplicate removed)*'''),
     
    (r'\[รูปภาพประกอบ \(ลบออกแล้ว\)\]\s*\(Figure 08: Source Code for standalone isolation software \(Reference: IQ-TC-06\)',
     '''```python
def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/aqr') # IQ-TC-06 Local Loopback (Offline)

if __name__ == '__main__':
    # Start the Flask app
    if getattr(sys, 'frozen', False):
        # Auto-open browser in EXE mode
        Timer(1.5, open_browser).start()
        serve(app, host='0.0.0.0', port=5000, threads=8, channel_timeout=3600) # IQ-TC-06 Localhost Isolation
```\n*(Figure 08: Source Code for standalone isolation software (Reference: IQ-TC-06)*'''),
     
    (r'\[รูปภาพประกอบ \(ลบออกแล้ว\)\]\s*\[รูปภาพประกอบ \(ลบออกแล้ว\)\]',
     '''```python
# GAMP 5: UR-DI-01 Verify audit trail integrity on startup (IQ-TC-07)
try:
    audit_valid, audit_msg = audit_trail.verify_audit_trail()
    if not audit_valid:
        # ERR-004: Audit Log Corrupt - System must refuse to start
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()  # Hide main window
        messagebox.showerror(
            "ERR-004",
            f"ERR-004: Audit Trail Integrity Check Failed\\n\\nDetails: {audit_msg}\\n\\nSystem execution halted due to security violation."
        )
        sys.exit(1) # IQ-TC-07: Halt system on integrity failure
except Exception as e:
    pass
```\n*(Figure 09: Source Code for Pre-Flight Integrity Check Failure (Reference: IQ-TC-07)*''')
]

for pattern, replacement in replacements:
    content = re.sub(pattern, replacement.replace('\\', '\\\\'), content)

with open(md_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Injected code snippets!")
