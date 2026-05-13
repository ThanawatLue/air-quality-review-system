# Build Instructions for Air Quality Review

## สำหรับผู้พัฒนา (Developer)

### ขั้นตอนการสร้างไฟล์ .exe (Building Executable)

#### 1. ตรวจสอบการติดตั้ง Python และ pip
- ตรวจสอบให้แน่ใจว่าได้ติดตั้ง Python (เวอร์ชัน 3.7 ขึ้นไป)
- เปิด Command Prompt และรัน:
  ```bash
  python --version
  pip --version
  ```

#### 2. ติดตั้ง Dependencies
- ไปยังโฟลเดอร์โปรเจกต์
- รันคำสั่ง:
  ```bash
  pip install -r requirements.txt
  ```

#### 3. ติดตั้ง PyInstaller
```bash
pip install pyinstaller
```

#### 4. สร้างไฟล์ .exe

**วิธีที่ 1: ใช้ Spec File (แนะนำ)**
```bash
pyinstaller app.spec
```

**วิธีที่ 2: ใช้ Command Line**
```bash
pyinstaller --onefile --windowed --add-data "templates;templates" --add-data "static;static" --add-data "data;data" app.py
```

**คำอธิบายพารามิเตอร์:**
- `--onefile`: รวมทุกอย่างไว้ในไฟล์ .exe ไฟล์เดียว
- `--windowed`: รันแอปโดยไม่มีหน้าต่างคอนโซล (GUI mode)
- `--add-data "templates;templates"`: รวมโฟลเดอร์ templates (สำคัญสำหรับ Flask)
- `--add-data "static;static"`: รวมโฟลเดอร์ static (CSS, JS)
- `--add-data "data;data"`: รวมโฟลเดอร์ data (ไฟล์ CSV และ Excel)

#### 5. หาไฟล์ที่สร้างเสร็จ
- ไฟล์ .exe จะอยู่ในโฟลเดอร์ `dist/`
- ชื่อไฟล์: `app.exe` หรือตามที่ระบุใน app.spec

#### 6. ทดสอบไฟล์ .exe
- คัดลอกไฟล์ .exe ไปยังโฟลเดอร์ที่ต้องการ
- สร้างโฟลเดอร์ `reports` ในตำแหน่งเดียวกับไฟล์ .exe
- ดับเบิลคลิกเพื่อรัน

## สำหรับผู้ใช้งาน (End User)

### การเตรียมคอมพิวเตอร์ก่อนใช้งาน

#### 1. ติดตั้ง Microsoft Visual C++ Redistributable (สำคัญมาก!)
- ข้อผิดพลาด `Failed to load Python DLL` มักเกิดจากการไม่มีส่วนประกอบนี้
- ดาวน์โหลดจาก: https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170
- เลือกเวอร์ชันที่เหมาะสม (ส่วนใหญ่ x64)
- ติดตั้งและรีสตาร์ทคอมพิวเตอร์

#### 2. เตรียมโฟลเดอร์สำหรับแอปพลิเคชัน
- สร้างโฟลเดอร์ใหม่สำหรับเก็บแอป (เช่น `C:\AirQualityReview`)
- คัดลอกไฟล์ `.exe` ไปยังโฟลเดอร์นี้
- สร้างโฟลเดอร์ `reports` ในตำแหน่งเดียวกับไฟล์ `.exe`

```
AirQualityReview/
├── app.exe
└── reports/        (โฟลเดอร์ว่างเปล่า - จำเป็นต้องมี)
```

#### 3. รันแอปพลิเคชัน
- ดับเบิลคลิกที่ไฟล์ `.exe`
- รอสักครู่ (อาจใช้เวลา 5-10 วินาทีในการเริ่มต้น)
- เบราว์เซอร์จะเปิดขึ้นอัตโนมัติที่ `http://127.0.0.1:5000/aqr`

#### 4. ใช้งานแอปพลิเคชัน
- เลือกโฟลเดอร์ที่มีไฟล์ CSV
- เลือกไฟล์ SetPointLimit.xlsx
- กำหนดช่วงวันที่และห้องที่ต้องการวิเคราะห์
- กดปุ่ม Analyze เพื่อเริ่มวิเคราะห์
- ไฟล์รายงานจะถูกบันทึกในโฟลเดอร์ `reports`

## ข้อควรระวัง

### สำหรับนักพัฒนา
- หลังจากแก้ไขโค้ด ต้อง build ใหม่ทุกครั้ง
- ตรวจสอบให้แน่ใจว่าไฟล์ใน `templates/`, `static/`, และ `data/` ถูกรวมอยู่ใน .exe
- ทดสอบ .exe บนคอมพิวเตอร์ที่ไม่มี Python ติดตั้ง

### สำหรับผู้ใช้
- ไม่ต้องติดตั้ง Python หรือไลบรารีใดๆ
- ต้องมี Microsoft Visual C++ Redistributable
- โฟลเดอร์ `reports` ต้องถูกสร้างไว้ก่อนรันแอป
- ไฟล์รายงานจะถูกบันทึกในโฟลเดอร์ `reports` เท่านั้น

## การแก้ปัญหา (Troubleshooting)

### ปัญหา: Failed to load Python DLL
- สาเหตุ: ไม่มี Microsoft Visual C++ Redistributable
- วิธีแก้: ติดตั้ง Microsoft Visual C++ Redistributable (x64)

### ปัญหา: แอปไม่เปิดขึ้น
- ตรวจสอบว่ามีโฟลเดอร์ `reports` หรือไม่
- ตรวจสอบว่ามีไฟล์ข้อมูลในโฟลเดอร์ `data/` หรือไม่
- ลองรันในโหมด administrator

### ปัญหา: หน้าเว็บไม่โหลด
- ตรวจสอบว่า port 5000 ไม่ถูกใช้งานโดยโปรแกรมอื่น
- รอสักครู่ แอปอาจใช้เวลาในการเริ่มต้น
- ตรวจสอบ firewall/antivirus

## ไฟล์ที่จำเป็นสำหรับการ Build

### ไฟล์ Source Code (ต้องมี)
- `app.py` - ไฟล์หลัก
- `analysis_logic.py` - โมดูลวิเคราะห์ข้อมูล

### โฟลเดอร์ข้อมูล (ต้องมี)
- `templates/` - HTML templates
- `static/` - CSS และ JavaScript
- `data/` - ไฟล์ข้อมูลตัวอย่าง

### ไฟล์ Configuration (ต้องมี)
- `app.spec` - PyInstaller configuration
- `requirements.txt` - Python dependencies

### ไฟล์เอกสาร (แนะนำ)
- `README.md` - คู่มือโดยรวม
- `BUILD_INSTRUCTIONS.md` - คู่มือการ build (ไฟล์นี้)
- `.gitignore` - ไฟล์ที่ไม่ต้องการให้เข้า Git

### Dependencies หลัก:
  - flask - Web framework
  - pandas - Data processing
  - plotly - Data visualization
  - openpyxl - Excel file handling
  - pyinstaller - Build tool
