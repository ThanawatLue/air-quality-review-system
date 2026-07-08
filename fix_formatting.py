import re

md_path = r"C:\Users\thana\My Drive\GPO\Appendix 2_Module\Appendix 2_Enclosure 1.md"

with open(md_path, "r", encoding="utf-8") as f:
    content = f.read()

# Exact escaped strings based on file viewing
replacements = [
    (r'__\[รูปภาพประกอบ \(ลบออกแล้ว\)\]__\s*\\\(Figure 01: Source Code for log\\_event Function \\\(Reference: CRR\\-TC\\-01\\\)', 
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
```\n*(Figure 01: Source Code for log_event Function (Reference: CRR-TC-01)*\n\n**รายละเอียดฟังก์ชัน (Function Details):**\n*   **ข้อมูลนำเข้า (Input):**\n    *   `action` (ข้อความ/String): บอกว่ากำลังทำอะไร เช่น "START_ANALYSIS"\n    *   `details` (ข้อความ/String): รายละเอียดเพิ่มเติม (ได้มาจากภายในโค้ดตอนที่โปรแกรมทำงาน)\n*   **ผลลัพธ์ (Output):**\n    *   ไม่มีการส่งค่ากลับ (None) แต่ผลที่ได้คือการบันทึกบรรทัดข้อมูลใหม่ลงในไฟล์ `audit_trail.log` อย่างถาวร\n*   **คำอธิบายการทำงาน (How it works):**\n    *   โปรแกรมจะดึงชื่อผู้ใช้งาน Windows (Username) ของคนที่กำลังใช้งานอยู่ ณ ขณะนั้น และดึงเวลาปัจจุบัน\n    *   จากนั้นจะนำข้อมูลทั้งหมดไปคำนวณรหัสลับ (Cryptographic Hash) ผูกติดกับข้อมูลบรรทัดก่อนหน้า แล้วบันทึกลงไฟล์ เพื่อให้มั่นใจได้ว่าประวัติการทำงานนี้มาจากผู้ใช้คนนี้จริงๆ และไม่สามารถถูกแก้ไขย้อนหลังได้'''),
    
    (r'\[รูปภาพประกอบ \(ลบออกแล้ว\)\]\s*\\\(Figure 02: Source Code for temporal alignment with 60s \\\(Reference: CRR\\-TC\\-01\\\)',
     '''```python
        # GAMP 5: Align mismatched sensor timestamps dynamically using merge_asof with a 60s tolerance window
        comparison_df = pd.merge_asof(
            df.sort_values("DateTime"),
            corridor_df.sort_values("DateTime")[["DateTime", "Pressure"]].rename(columns={"Pressure": "Corridor_Pressure"}),
            on="DateTime",
            direction="nearest",
            tolerance=pd.Timedelta("60s")
        )
```\n*(Figure 02: Source Code for temporal alignment with 60s (Reference: CRR-TC-02)*\n\n**รายละเอียดฟังก์ชัน (Function Details):**\n*   **ข้อมูลนำเข้า (Input):**\n    *   ตารางข้อมูลความดันของห้อง (`df` / DataFrame): ได้มาจากการอ่านไฟล์ CSV ของห้องนั้นๆ\n    *   ตารางข้อมูลความดันของทางเดินเปรียบเทียบ (`corridor_df` / DataFrame): ได้มาจากการอ่านไฟล์ CSV ของห้องที่เป็นทางเดิน (Corridor)\n*   **ผลลัพธ์ (Output):**\n    *   ตารางข้อมูลใหม่ (`comparison_df` / DataFrame): เป็นตารางที่นำข้อมูลของ 2 ห้องมาประกบติดกันเรียบร้อยแล้ว\n*   **คำอธิบายการทำงาน (How it works):**\n    *   ในโลกความเป็นจริง เซนเซอร์แต่ละตัวอาจจะส่งข้อมูลมาในเวลาที่ไม่ตรงกันเป๊ะในระดับวินาที\n    *   ฟังก์ชัน `merge_asof` จะทำหน้าที่ "จับคู่" ข้อมูลเวลาที่ใกล้เคียงกันที่สุดของสองตาราง โดยอนุโลมให้เวลาคลาดเคลื่อนกันได้ไม่เกิน 60 วินาที (`tolerance=pd.Timedelta("60s")`)\n    *   ทำให้เราสามารถเอาค่าความดันของ 2 ห้องมาลบกันเพื่อตรวจสอบความผิดปกติได้ แม้เวลาในไฟล์ CSV จะเหลื่อมกันเล็กน้อย'''),
    
    (r'\[รูปภาพประกอบ \(ลบออกแล้ว\)\]\s*\\\(Figure 03: Source Code for temporal alignment with 60s \\\(Reference: CRR\\-TC\\-01\\\)',
     '''*(Figure 03 removed - Duplicate)*'''),
     
    (r'\[รูปภาพประกอบ \(ลบออกแล้ว\)\]\s*\\\(Figure 04: Source Code for software version identify \\\(Reference: IQ\\-TC\\-01\\\)',
     '''```python
                # GAMP 5: UR-FN-08 Hardcode version and generation date (IQ-TC-01)
                ws.write(0, last_col, f'Software Version: v1.1.0\\nGenerated: {time.strftime("%Y-%m-%d %H:%M")}', fmt_center)
```\n*(Figure 04: Source Code for software version identify (Reference: IQ-TC-01)*\n\n**รายละเอียดฟังก์ชัน (Function Details):**\n*   **ข้อมูลนำเข้า (Input):**\n    *   เลขเวอร์ชันซอฟต์แวร์: เป็นข้อความตายตัว "v1.1.0"\n    *   เวลาปัจจุบัน (`time.strftime`): ดึงมาจากเวลาของเครื่องคอมพิวเตอร์\n*   **ผลลัพธ์ (Output):**\n    *   ข้อความที่ถูกประทับตรารางวัลลงในไฟล์รายงาน Excel \n*   **คำอธิบายการทำงาน (How it works):**\n    *   เมื่อโปรแกรมวิเคราะห์ข้อมูลเสร็จและกำลังสร้างรายงาน Excel โค้ดส่วนนี้จะถูกเรียกใช้เพื่อเขียนข้อความบังคับลงในช่องเซลล์หัวมุมขวาบนของรายงาน\n    *   โดยจะพิมพ์ "Software Version: v1.1.0" และ "เวลาที่สร้างรายงาน" ลงไปเสมอ เพื่อให้ Auditor หรือผู้ตรวจสามารถยืนยันได้ว่ารายงานฉบับนี้ถูกสร้างจากซอฟต์แวร์เวอร์ชันที่ผ่านการทำ Validation อย่างถูกต้อง'''),
     
    (r'\[รูปภาพประกอบ \(ลบออกแล้ว\)\]\s*\\\(Figure 05: Source Code for software version identify \\\(Reference: IQ\\-TC\\-01\\\)',
     '''*(Figure 05 removed - Duplicate)*'''),
     
    (r'\[รูปภาพประกอบ \(ลบออกแล้ว\)\]\s*\\\(Figure 06: Source Code for automatically creating folders and the core security log file \\\(Reference: IQ\\-TC\\-02 and IQ\\-TC\\-04\\\)',
     '''```python
# GAMP 5: Reports directory setup
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')
if not os.path.exists(REPORTS_DIR):
    os.makedirs(REPORTS_DIR)

# GAMP 5: Logs directory setup (UR-DI-01, IQ-TC-02, IQ-TC-04)
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)
```\n*(Figure 06: Source Code for automatically creating folders and the core security log file (Reference: IQ-TC-02 and IQ-TC-04)*\n\n**รายละเอียดฟังก์ชัน (Function Details):**\n*   **ข้อมูลนำเข้า (Input):**\n    *   ตำแหน่งพาธของโฟลเดอร์ปัจจุบันที่โปรแกรมทำงานอยู่ (`BASE_DIR`) เพื่อใช้ตั้งชื่อโฟลเดอร์ `reports` และ `logs`\n*   **ผลลัพธ์ (Output):**\n    *   โฟลเดอร์เปล่าๆ ที่ถูกสร้างขึ้นจริงบนคอมพิวเตอร์ หากยังไม่มี\n*   **คำอธิบายการทำงาน (How it works):**\n    *   ก่อนที่ระบบหลักจะเริ่มทำงาน โปรแกรมจะตรวจสอบด้วยคำสั่ง `os.path.exists` ว่ามีโฟลเดอร์รายงานและโฟลเดอร์ล็อกอยู่หรือยัง\n    *   ถ้าพบว่าไม่มี (เช่น ใช้งานครั้งแรก หรือมีผู้ใช้เผลอลบโฟลเดอร์ทิ้งไป) ระบบจะใช้คำสั่ง `os.makedirs` เพื่อสร้างโฟลเดอร์เหล่านั้นขึ้นมาใหม่โดยอัตโนมัติ \n    *   คุณสมบัติ Self-healing นี้ช่วยป้องกันไม่ให้โปรแกรมทำงานล้มเหลวเวลาที่มันพยายามจะบันทึกไฟล์'''),
     
    (r'\[รูปภาพประกอบ \(ลบออกแล้ว\)\]\s*\\\(Figure 07: Source Code for automatically creating folders and the core security log file \\\(Reference: IQ\\-TC\\-02 and IQ\\-TC\\-04\\\)',
     '''*(Figure 07 removed - Duplicate)*'''),
     
    (r'\[รูปภาพประกอบ \(ลบออกแล้ว\)\]\s*\\\(Figure 08: Source Code for standalone isolation software \\\(Reference: IQ\\-TC\\-06\\\)',
     '''```python
def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/aqr') # IQ-TC-06 Local Loopback (Offline)

if __name__ == '__main__':
    # Start the Flask app
    if getattr(sys, 'frozen', False):
        # Auto-open browser in EXE mode
        Timer(1.5, open_browser).start()
        serve(app, host='0.0.0.0', port=5000, threads=8, channel_timeout=3600) # IQ-TC-06 Localhost Isolation
```\n*(Figure 08: Source Code for standalone isolation software (Reference: IQ-TC-06)*\n\n**รายละเอียดฟังก์ชัน (Function Details):**\n*   **ข้อมูลนำเข้า (Input):**\n    *   สถานะของโปรแกรม (`sys.frozen` / Boolean): เพื่อเช็คว่าผู้ใช้เปิดโปรแกรมจากโค้ด Python โดยตรง หรือเปิดผ่านไฟล์ `.exe`\n*   **ผลลัพธ์ (Output):**\n    *   การเปิดหน้าต่าง Web Browser และการรัน Local Web Server\n*   **คำอธิบายการทำงาน (How it works):**\n    *   ระบบนี้เป็นแอปพลิเคชันเดสก์ท็อปที่จำลองตัวเองเป็นเว็บไซต์ โค้ดส่วนนี้จะตรวจสอบว่าถ้าโปรแกรมรันจากไฟล์ `.exe` จะทำการตั้งเวลา (1.5 วินาที) ให้เปิดหน้า Web Browser ขึ้นมาอัตโนมัติ\n    *   จากนั้นจะเปิดระบบเซิร์ฟเวอร์ย่อยชื่อ Waitress (`serve(...)`) แบบออฟไลน์ (พอร์ต 5000) อยู่ภายในเครื่องคอมพิวเตอร์ของคุณเอง\n    *   แปลว่าโปรแกรมทำงานได้แบบเป็นเอกเทศสมบูรณ์ (Standalone) โดยไม่ต้องเชื่อมต่ออินเทอร์เน็ตหรือมีซอฟต์แวร์ฐานข้อมูลใดๆ ภายนอกเลย''')
]

for pattern, replacement in replacements:
    content = re.sub(pattern, replacement.replace('\\', '\\\\'), content)

with open(md_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Fixed formatting!")
