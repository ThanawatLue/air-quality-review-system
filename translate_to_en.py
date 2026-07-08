import re

md_path = r"C:\Users\thana\My Drive\GPO\Appendix 2_Module\Appendix 2_Enclosure 1.md"

with open(md_path, "r", encoding="utf-8") as f:
    content = f.read()

translations = [
    (
'''**รายละเอียดฟังก์ชัน (Function Details):**
*   **ข้อมูลนำเข้า (Input):**
    *   `action` (ข้อความ/String): บอกว่ากำลังทำอะไร เช่น "START_ANALYSIS"
    *   `details` (ข้อความ/String): รายละเอียดเพิ่มเติม (ได้มาจากภายในโค้ดตอนที่โปรแกรมทำงาน)
*   **ผลลัพธ์ (Output):**
    *   ไม่มีการส่งค่ากลับ (None) แต่ผลที่ได้คือการบันทึกบรรทัดข้อมูลใหม่ลงในไฟล์ `audit_trail.log` อย่างถาวร
*   **คำอธิบายการทำงาน (How it works):**
    *   โปรแกรมจะดึงชื่อผู้ใช้งาน Windows (Username) ของคนที่กำลังใช้งานอยู่ ณ ขณะนั้น และดึงเวลาปัจจุบัน
    *   จากนั้นจะนำข้อมูลทั้งหมดไปคำนวณรหัสลับ (Cryptographic Hash) ผูกติดกับข้อมูลบรรทัดก่อนหน้า แล้วบันทึกลงไฟล์ เพื่อให้มั่นใจได้ว่าประวัติการทำงานนี้มาจากผู้ใช้คนนี้จริงๆ และไม่สามารถถูกแก้ไขย้อนหลังได้''',
'''**Function Details:**
*   **Input:**
    *   `action` (String): What the system is doing, for example, "START_ANALYSIS".
    *   `details` (String): Extra information about the action.
*   **Output:**
    *   It returns nothing (None). It simply writes a new line into the `audit_trail.log` file permanently.
*   **How it works:**
    *   The program finds the Windows username of the person using the computer right now. It also gets the current time.
    *   Then, it mixes this information with a secret code (Cryptographic Hash) from the previous line. It saves this to the file. This makes sure we know exactly who did the action, and nobody can change the history later.'''
    ),
    (
'''**รายละเอียดฟังก์ชัน (Function Details):**
*   **ข้อมูลนำเข้า (Input):**
    *   ตารางข้อมูลความดันของห้อง (`df` / DataFrame): ได้มาจากการอ่านไฟล์ CSV ของห้องนั้นๆ
    *   ตารางข้อมูลความดันของทางเดินเปรียบเทียบ (`corridor_df` / DataFrame): ได้มาจากการอ่านไฟล์ CSV ของห้องที่เป็นทางเดิน (Corridor)
*   **ผลลัพธ์ (Output):**
    *   ตารางข้อมูลใหม่ (`comparison_df` / DataFrame): เป็นตารางที่นำข้อมูลของ 2 ห้องมาประกบติดกันเรียบร้อยแล้ว
*   **คำอธิบายการทำงาน (How it works):**
    *   ในโลกความเป็นจริง เซนเซอร์แต่ละตัวอาจจะส่งข้อมูลมาในเวลาที่ไม่ตรงกันเป๊ะในระดับวินาที
    *   ฟังก์ชัน `merge_asof` จะทำหน้าที่ "จับคู่" ข้อมูลเวลาที่ใกล้เคียงกันที่สุดของสองตาราง โดยอนุโลมให้เวลาคลาดเคลื่อนกันได้ไม่เกิน 60 วินาที (`tolerance=pd.Timedelta("60s")`)
    *   ทำให้เราสามารถเอาค่าความดันของ 2 ห้องมาลบกันเพื่อตรวจสอบความผิดปกติได้ แม้เวลาในไฟล์ CSV จะเหลื่อมกันเล็กน้อย''',
'''**Function Details:**
*   **Input:**
    *   Room pressure data table (`df` / DataFrame): Read from the room's CSV file.
    *   Corridor pressure data table (`corridor_df` / DataFrame): Read from the corridor's CSV file.
*   **Output:**
    *   A new data table (`comparison_df` / DataFrame): A table that combines the data from both rooms together.
*   **How it works:**
    *   In the real world, sensors do not always send data at the exact same second.
    *   The `merge_asof` function pairs the closest times from both tables. It allows a small time difference of up to 60 seconds (`tolerance=pd.Timedelta("60s")`).
    *   This allows us to subtract the pressure values of the two rooms to find problems, even if the times in the CSV files do not match exactly.'''
    ),
    (
'''**รายละเอียดฟังก์ชัน (Function Details):**
*   **ข้อมูลนำเข้า (Input):**
    *   เลขเวอร์ชันซอฟต์แวร์: เป็นข้อความตายตัว "v1.1.0"
    *   เวลาปัจจุบัน (`time.strftime`): ดึงมาจากเวลาของเครื่องคอมพิวเตอร์
*   **ผลลัพธ์ (Output):**
    *   ข้อความที่ถูกประทับตรารางวัลลงในไฟล์รายงาน Excel 
*   **คำอธิบายการทำงาน (How it works):**
    *   เมื่อโปรแกรมวิเคราะห์ข้อมูลเสร็จและกำลังสร้างรายงาน Excel โค้ดส่วนนี้จะถูกเรียกใช้เพื่อเขียนข้อความบังคับลงในช่องเซลล์หัวมุมขวาบนของรายงาน
    *   โดยจะพิมพ์ "Software Version: v1.1.0" และ "เวลาที่สร้างรายงาน" ลงไปเสมอ เพื่อให้ Auditor หรือผู้ตรวจสามารถยืนยันได้ว่ารายงานฉบับนี้ถูกสร้างจากซอฟต์แวร์เวอร์ชันที่ผ่านการทำ Validation อย่างถูกต้อง''',
'''**Function Details:**
*   **Input:**
    *   Software version number: A fixed text "v1.1.0".
    *   Current time (`time.strftime`): Gets the time from the computer.
*   **Output:**
    *   A text stamp written into the Excel report file.
*   **How it works:**
    *   When the program finishes checking the data and creates the Excel report, it uses this code to write a mandatory message in the top right corner of the report.
    *   It will always print "Software Version: v1.1.0" and the exact time the report was created. This helps the Auditor confirm that the report was made by the correct, validated software version.'''
    ),
    (
'''**รายละเอียดฟังก์ชัน (Function Details):**
*   **ข้อมูลนำเข้า (Input):**
    *   ตำแหน่งพาธของโฟลเดอร์ปัจจุบันที่โปรแกรมทำงานอยู่ (`BASE_DIR`) เพื่อใช้ตั้งชื่อโฟลเดอร์ `reports` และ `logs`
*   **ผลลัพธ์ (Output):**
    *   โฟลเดอร์เปล่าๆ ที่ถูกสร้างขึ้นจริงบนคอมพิวเตอร์ หากยังไม่มี
*   **คำอธิบายการทำงาน (How it works):**
    *   ก่อนที่ระบบหลักจะเริ่มทำงาน โปรแกรมจะตรวจสอบด้วยคำสั่ง `os.path.exists` ว่ามีโฟลเดอร์รายงานและโฟลเดอร์ล็อกอยู่หรือยัง
    *   ถ้าพบว่าไม่มี (เช่น ใช้งานครั้งแรก หรือมีผู้ใช้เผลอลบโฟลเดอร์ทิ้งไป) ระบบจะใช้คำสั่ง `os.makedirs` เพื่อสร้างโฟลเดอร์เหล่านั้นขึ้นมาใหม่โดยอัตโนมัติ 
    *   คุณสมบัติ Self-healing นี้ช่วยป้องกันไม่ให้โปรแกรมทำงานล้มเหลวเวลาที่มันพยายามจะบันทึกไฟล์''',
'''**Function Details:**
*   **Input:**
    *   The current folder path where the program is running (`BASE_DIR`). This is used to name the `reports` and `logs` folders.
*   **Output:**
    *   Empty folders created on the computer, if they do not exist already.
*   **How it works:**
    *   Before the main system starts, the program checks if the reports and logs folders exist using the `os.path.exists` command.
    *   If they are missing (for example, on the first use, or if a user deleted them by mistake), the system automatically creates them using the `os.makedirs` command.
    *   This self-healing feature prevents the program from crashing when it tries to save a file later.'''
    ),
    (
'''**รายละเอียดฟังก์ชัน (Function Details):**
*   **ข้อมูลนำเข้า (Input):**
    *   สถานะของโปรแกรม (`sys.frozen` / Boolean): เพื่อเช็คว่าผู้ใช้เปิดโปรแกรมจากโค้ด Python โดยตรง หรือเปิดผ่านไฟล์ `.exe`
*   **ผลลัพธ์ (Output):**
    *   การเปิดหน้าต่าง Web Browser และการรัน Local Web Server
*   **คำอธิบายการทำงาน (How it works):**
    *   ระบบนี้เป็นแอปพลิเคชันเดสก์ท็อปที่จำลองตัวเองเป็นเว็บไซต์ โค้ดส่วนนี้จะตรวจสอบว่าถ้าโปรแกรมรันจากไฟล์ `.exe` จะทำการตั้งเวลา (1.5 วินาที) ให้เปิดหน้า Web Browser ขึ้นมาอัตโนมัติ
    *   จากนั้นจะเปิดระบบเซิร์ฟเวอร์ย่อยชื่อ Waitress (`serve(...)`) แบบออฟไลน์ (พอร์ต 5000) อยู่ภายในเครื่องคอมพิวเตอร์ของคุณเอง
    *   แปลว่าโปรแกรมทำงานได้แบบเป็นเอกเทศสมบูรณ์ (Standalone) โดยไม่ต้องเชื่อมต่ออินเทอร์เน็ตหรือมีซอฟต์แวร์ฐานข้อมูลใดๆ ภายนอกเลย''',
'''**Function Details:**
*   **Input:**
    *   Program status (`sys.frozen` / Boolean): Checks if the user opened the program directly from Python code or from an `.exe` file.
*   **Output:**
    *   Opens a web browser window and runs a local web server.
*   **How it works:**
    *   This system is a desktop application that acts like a website. This part of the code checks if the program is running from an `.exe` file. If yes, it sets a timer (1.5 seconds) to open the web browser automatically.
    *   Then, it starts a small offline server called Waitress (`serve(...)`) on port 5000 inside your own computer.
    *   This means the program works completely on its own (Standalone). It does not need the internet or any outside database software to run.'''
    )
]

for th_text, en_text in translations:
    content = content.replace(th_text, en_text)

with open(md_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Translated successfully!")
