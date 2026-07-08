import re

md_path = r"C:\Users\thana\My Drive\GPO\Appendix 2_Module\Appendix 2_Enclosure 1.md"

with open(md_path, "r", encoding="utf-8") as f:
    content = f.read()

# Define the explanation texts
explanations = {
    r'\*\(Figure 01: Source Code for log_event Function \(Reference: CRR-TC-01\)\*':
"""*(Figure 01: Source Code for log_event Function (Reference: CRR-TC-01)*

**รายละเอียดฟังก์ชัน (Function Details):**
*   **ข้อมูลนำเข้า (Input):**
    *   `action` (ข้อความ/String): บอกว่ากำลังทำอะไร เช่น "START_ANALYSIS"
    *   `details` (ข้อความ/String): รายละเอียดเพิ่มเติม (ได้มาจากภายในโค้ดตอนที่โปรแกรมทำงาน)
*   **ผลลัพธ์ (Output):**
    *   ไม่มีการส่งค่ากลับ (None) แต่ผลที่ได้คือการบันทึกบรรทัดข้อมูลใหม่ลงในไฟล์ `audit_trail.log` อย่างถาวร
*   **คำอธิบายการทำงาน (How it works):**
    *   โปรแกรมจะดึงชื่อผู้ใช้งาน Windows (Username) ของคนที่กำลังใช้งานอยู่ ณ ขณะนั้น และดึงเวลาปัจจุบัน
    *   จากนั้นจะนำข้อมูลทั้งหมดไปคำนวณรหัสลับ (Cryptographic Hash) ผูกติดกับข้อมูลบรรทัดก่อนหน้า แล้วบันทึกลงไฟล์ เพื่อให้มั่นใจได้ว่าประวัติการทำงานนี้มาจากผู้ใช้คนนี้จริงๆ และไม่สามารถถูกแก้ไขย้อนหลังได้""",
    
    r'\*\(Figure 02: Source Code for temporal alignment with 60s \(Reference: CRR-TC-02\)\*':
"""*(Figure 02: Source Code for temporal alignment with 60s (Reference: CRR-TC-02)*

**รายละเอียดฟังก์ชัน (Function Details):**
*   **ข้อมูลนำเข้า (Input):**
    *   ตารางข้อมูลความดันของห้อง (`df` / DataFrame): ได้มาจากการอ่านไฟล์ CSV ของห้องนั้นๆ
    *   ตารางข้อมูลความดันของทางเดินเปรียบเทียบ (`corridor_df` / DataFrame): ได้มาจากการอ่านไฟล์ CSV ของห้องที่เป็นทางเดิน (Corridor)
*   **ผลลัพธ์ (Output):**
    *   ตารางข้อมูลใหม่ (`comparison_df` / DataFrame): เป็นตารางที่นำข้อมูลของ 2 ห้องมาประกบติดกันเรียบร้อยแล้ว
*   **คำอธิบายการทำงาน (How it works):**
    *   ในโลกความเป็นจริง เซนเซอร์แต่ละตัวอาจจะส่งข้อมูลมาในเวลาที่ไม่ตรงกันเป๊ะในระดับวินาที
    *   ฟังก์ชัน `merge_asof` จะทำหน้าที่ "จับคู่" ข้อมูลเวลาที่ใกล้เคียงกันที่สุดของสองตาราง โดยอนุโลมให้เวลาคลาดเคลื่อนกันได้ไม่เกิน 60 วินาที (`tolerance=pd.Timedelta("60s")`)
    *   ทำให้เราสามารถเอาค่าความดันของ 2 ห้องมาลบกันเพื่อตรวจสอบความผิดปกติได้ แม้เวลาในไฟล์ CSV จะเหลื่อมกันเล็กน้อย""",
    
    r'\*\(Figure 04: Source Code for software version identify \(Reference: IQ-TC-01\)\*':
"""*(Figure 04: Source Code for software version identify (Reference: IQ-TC-01)*

**รายละเอียดฟังก์ชัน (Function Details):**
*   **ข้อมูลนำเข้า (Input):**
    *   เลขเวอร์ชันซอฟต์แวร์: เป็นข้อความตายตัว "v1.1.0"
    *   เวลาปัจจุบัน (`time.strftime`): ดึงมาจากเวลาของเครื่องคอมพิวเตอร์
*   **ผลลัพธ์ (Output):**
    *   ข้อความที่ถูกประทับตรารางวัลลงในไฟล์รายงาน Excel 
*   **คำอธิบายการทำงาน (How it works):**
    *   เมื่อโปรแกรมวิเคราะห์ข้อมูลเสร็จและกำลังสร้างรายงาน Excel โค้ดส่วนนี้จะถูกเรียกใช้เพื่อเขียนข้อความบังคับลงในช่องเซลล์หัวมุมขวาบนของรายงาน
    *   โดยจะพิมพ์ "Software Version: v1.1.0" และ "เวลาที่สร้างรายงาน" ลงไปเสมอ เพื่อให้ Auditor หรือผู้ตรวจสามารถยืนยันได้ว่ารายงานฉบับนี้ถูกสร้างจากซอฟต์แวร์เวอร์ชันที่ผ่านการทำ Validation อย่างถูกต้อง""",
    
    r'\*\(Figure 06: Source Code for automatically creating folders and the core security log file \(Reference: IQ-TC-02 and IQ-TC-04\)\*':
"""*(Figure 06: Source Code for automatically creating folders and the core security log file (Reference: IQ-TC-02 and IQ-TC-04)*

**รายละเอียดฟังก์ชัน (Function Details):**
*   **ข้อมูลนำเข้า (Input):**
    *   ตำแหน่งพาธของโฟลเดอร์ปัจจุบันที่โปรแกรมทำงานอยู่ (`BASE_DIR`) เพื่อใช้ตั้งชื่อโฟลเดอร์ `reports` และ `logs`
*   **ผลลัพธ์ (Output):**
    *   โฟลเดอร์เปล่าๆ ที่ถูกสร้างขึ้นจริงบนคอมพิวเตอร์ หากยังไม่มี
*   **คำอธิบายการทำงาน (How it works):**
    *   ก่อนที่ระบบหลักจะเริ่มทำงาน โปรแกรมจะตรวจสอบด้วยคำสั่ง `os.path.exists` ว่ามีโฟลเดอร์รายงานและโฟลเดอร์ล็อกอยู่หรือยัง
    *   ถ้าพบว่าไม่มี (เช่น ใช้งานครั้งแรก หรือมีผู้ใช้เผลอลบโฟลเดอร์ทิ้งไป) ระบบจะใช้คำสั่ง `os.makedirs` เพื่อสร้างโฟลเดอร์เหล่านั้นขึ้นมาใหม่โดยอัตโนมัติ 
    *   คุณสมบัติ Self-healing นี้ช่วยป้องกันไม่ให้โปรแกรมทำงานล้มเหลวเวลาที่มันพยายามจะบันทึกไฟล์""",
    
    r'\*\(Figure 08: Source Code for standalone isolation software \(Reference: IQ-TC-06\)\*':
"""*(Figure 08: Source Code for standalone isolation software (Reference: IQ-TC-06)*

**รายละเอียดฟังก์ชัน (Function Details):**
*   **ข้อมูลนำเข้า (Input):**
    *   สถานะของโปรแกรม (`sys.frozen` / Boolean): เพื่อเช็คว่าผู้ใช้เปิดโปรแกรมจากโค้ด Python โดยตรง หรือเปิดผ่านไฟล์ `.exe`
*   **ผลลัพธ์ (Output):**
    *   การเปิดหน้าต่าง Web Browser และการรัน Local Web Server
*   **คำอธิบายการทำงาน (How it works):**
    *   ระบบนี้เป็นแอปพลิเคชันเดสก์ท็อปที่จำลองตัวเองเป็นเว็บไซต์ โค้ดส่วนนี้จะตรวจสอบว่าถ้าโปรแกรมรันจากไฟล์ `.exe` จะทำการตั้งเวลา (1.5 วินาที) ให้เปิดหน้า Web Browser ขึ้นมาอัตโนมัติ
    *   จากนั้นจะเปิดระบบเซิร์ฟเวอร์ย่อยชื่อ Waitress (`serve(...)`) แบบออฟไลน์ (พอร์ต 5000) อยู่ภายในเครื่องคอมพิวเตอร์ของคุณเอง
    *   แปลว่าโปรแกรมทำงานได้แบบเป็นเอกเทศสมบูรณ์ (Standalone) โดยไม่ต้องเชื่อมต่ออินเทอร์เน็ตหรือมีซอฟต์แวร์ฐานข้อมูลใดๆ ภายนอกเลย""",
    
    r'\*\(Figure 09: Source Code for Pre-Flight Integrity Check Failure \(Reference: IQ-TC-07\)\*':
"""*(Figure 09: Source Code for Pre-Flight Integrity Check Failure (Reference: IQ-TC-07)*

**รายละเอียดฟังก์ชัน (Function Details):**
*   **ข้อมูลนำเข้า (Input):**
    *   ผลการตรวจสอบจากระบบ Audit Trail (`audit_valid` / Boolean): ถ้าเป็น True คือไฟล์ปกติ, ถ้าเป็น False คือไฟล์ถูกดัดแปลง
*   **ผลลัพธ์ (Output):**
    *   หากไฟล์ถูกดัดแปลง จะมีกล่องแจ้งเตือนความผิดพลาด (Message Box) ปรากฏขึ้น และโปรแกรมจะปิดตัวเองทันที (`sys.exit`)
*   **คำอธิบายการทำงาน (How it works):**
    *   นี่คือระบบป้องกันตัวเองของโปรแกรม เมื่อคุณดับเบิลคลิกเปิดโปรแกรม มันจะทำการอ่านไฟล์ประวัติการใช้งาน (`audit_trail.log`) แล้วคำนวณรหัสลับ (Hash) ของทุกบรรทัดใหม่ทั้งหมด
    *   หากมีคนแอบเปิดไฟล์ Log ด้วย Notepad แล้วแก้ข้อความหรือลบข้อมูลทิ้ง รหัสที่คำนวณได้จะไม่ตรงกับที่บันทึกไว้
    *   ระบบจะเด้งกล่องข้อความเตือนภัยและหยุดการทำงานทั้งหมดทันที เพื่อรักษามาตรฐานความปลอดภัยของข้อมูล (Data Integrity)"""
}

# Perform replacements
for pattern, replacement in explanations.items():
    content = re.sub(pattern, replacement, content)

with open(md_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Injected explanations!")
