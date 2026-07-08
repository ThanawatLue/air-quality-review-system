import re

md_path = r"C:\Users\thana\My Drive\GPO\Appendix 2_Module\Appendix 2_Enclosure 1.md"

with open(md_path, "r", encoding="utf-8") as f:
    content = f.read()

translations = [
    (
'''**รายละเอียดฟังก์ชัน (Function Details):**
*   **ข้อมูลนำเข้า (Input):**
    *   ผลการตรวจสอบจากระบบ Audit Trail (`audit_valid` / Boolean): ถ้าเป็น True คือไฟล์ปกติ, ถ้าเป็น False คือไฟล์ถูกดัดแปลง
*   **ผลลัพธ์ (Output):**
    *   หากไฟล์ถูกดัดแปลง จะมีกล่องแจ้งเตือนความผิดพลาด (Message Box) ปรากฏขึ้น และโปรแกรมจะปิดตัวเองทันที (`sys.exit`)
*   **คำอธิบายการทำงาน (How it works):**
    *   นี่คือระบบป้องกันตัวเองของโปรแกรม เมื่อคุณดับเบิลคลิกเปิดโปรแกรม มันจะทำการอ่านไฟล์ประวัติการใช้งาน (`audit_trail.log`) แล้วคำนวณรหัสลับ (Hash) ของทุกบรรทัดใหม่ทั้งหมด
    *   หากมีคนแอบเปิดไฟล์ Log ด้วย Notepad แล้วแก้ข้อความหรือลบข้อมูลทิ้ง รหัสที่คำนวณได้จะไม่ตรงกับที่บันทึกไว้
    *   ระบบจะเด้งกล่องข้อความเตือนภัยและหยุดการทำงานทั้งหมดทันที เพื่อรักษามาตรฐานความปลอดภัยของข้อมูล (Data Integrity)''',
'''**Function Details:**
*   **Input:**
    *   The check result from the Audit Trail system (`audit_valid` / Boolean): If True, the file is normal. If False, the file has been tampered with.
*   **Output:**
    *   If the file was tampered with, an error message box appears and the program shuts down immediately (`sys.exit`).
*   **How it works:**
    *   This is the program's self-protection system. When you open the program, it reads the entire history file (`audit_trail.log`) and recalculates the secret code (Hash) for every single line.
    *   If someone secretly opened the log file with Notepad and changed or deleted the text, the new calculated code will not match the saved code.
    *   The system will show a warning message and stop working immediately to keep the data safe and secure (Data Integrity).'''
    )
]

for th_text, en_text in translations:
    content = content.replace(th_text, en_text)

with open(md_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Translated IQ-TC-07 successfully!")
