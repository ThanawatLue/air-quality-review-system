# Project Structure Documentation

## ไฟล์ที่จำเป็นสำหรับการ Build .exe

### 1. Source Files (ไฟล์ต้นฉบับ Python)

#### app.py
- **คำอธิบาย**: ไฟล์หลักของแอปพลิเคชัน Flask
- **หน้าที่**:
  - จัดการ routing ของเว็บแอป
  - เชื่อมต่อกับ frontend (HTML templates)
  - เรียกใช้ analysis_logic
- **Dependencies**: Flask, pandas, tkinter, analysis_logic
- **หมายเหตุ**: AI module (agent_module) ถูก comment out และลบออกแล้ว

#### analysis_logic.py
- **คำอธิบาย**: โมดูลสำหรับวิเคราะห์ข้อมูล
- **หน้าที่**:
  - อ่านและประมวลผลไฟล์ CSV
  - เปรียบเทียบข้อมูลกับค่า limit
  - สร้างกราฟและรายงาน
- **Dependencies**: pandas, plotly, openpyxl

#### audit_trail.py
- **คำอธิบาย**: โมดูลความปลอดภัยและระบบบันทึก Audit Trail ตามข้อกำหนด GAMP 5 และ 21 CFR Part 11
- **หน้าที่**:
  - บันทึกประวัติการทำงานของระบบ (Audit Trail Log) ในรูปแบบ JSONL
  - สร้างและตรวจสอบ Cryptographic Hash-Chain (SHA-256) เพื่อยืนยันความสมบูรณ์ของข้อมูลและป้องกันการดัดแปลง (Tamper-Proof)
  - ทำการตรวจสอบแบบ Pre-flight Verification ในตอนเริ่มต้นเซิร์ฟเวอร์
- **Dependencies**: hashlib, json, datetime, os

#### agent_module.py (ถูกลบออกแล้ว)
- **คำอธิบาย**: โมดูล AI สำหรับการทบทวนข้อมูล
- **สถานะ**: ถูก comment out และลบออกจากโปรเจกต์แล้ว
- **Dependencies เดิม**: google-genai, python-docx, Pillow, plotly

### 2. Configuration Files (ไฟล์การตั้งค่า)

#### AQR_Dashboard_v1.1.0_Fix.spec
- **คำอธิบาย**: Configuration file สำหรับ PyInstaller
- **หน้าที่**: กำหนดวิธีการ build .exe
- **สิ่งสำคัญ**: ระบุ data folders ที่ต้องรวม (templates, static, data) และ documentation ต่าง ๆ

#### requirements.txt
- **คำอธิบาย**: รายชื่อ Python packages ที่จำเป็น
- **หน้าที่**: ใช้สำหรับติดตั้ง dependencies อัตโนมัติ
- **Dependencies หลัก**:
  - flask - Web framework
  - waitress - Production WSGI server
  - pandas - Data processing
  - openpyxl - Excel file handling (Read)
  - xlsxwriter - Excel file handling (Write)
  - pyinstaller - Build tool

### 3. Data Folders (โฟลเดอร์ข้อมูล)

#### templates/
- **คำอธิบาย**: HTML templates สำหรับ Flask
- **ไฟล์ที่ต้องมี**:
  - `aqr.html` - หน้าหลัก Air Quality Review
  - `transform.html` - หน้า Data Transformation
  - `audit_trail.html` - หน้าจัดการและแสดงผลข้อมูลประวัติระบบ (Audit Trail Viewer) ตามข้อกำหนด GAMP 5
  - `index.html` - หน้าแรก
- **ไฟล์ที่ถูกลบ**:
  - `ai_review.html` - หน้า AI Review (ถูกลบออกแล้ว)

#### static/
- **คำอธิบาย**: Static files (CSS, JavaScript)
- **ไฟล์ที่ต้องมี**:
  - `style.css` - สไตล์ของเว็บแอป
  - `script.js` - JavaScript logic สำหรับ frontend

#### data/
- **คำอธิบาย**: ไฟล์ข้อมูลตัวอย่างและ limit files
- **ไฟล์ที่ต้องมี**:
  - `SetPointLimit.xlsx` - ไฟล์ค่า limit สำหรับการวิเคราะห์
  - ไฟล์ CSV ตัวอย่าง (ถ้าต้องการให้แอปมีข้อมูลเริ่มต้น)

### 4. Documentation Files (ไฟล์เอกสาร)

#### README.md
- **คำอธิบาย**: คู่มือโดยรวมของโปรเจกต์
- **เนื้อหา**: 
  - วิธีการติดตั้ง
  - วิธีการใช้งาน
  - คำอธิบายฟีเจอร์ต่างๆ

#### BUILD_INSTRUCTIONS.md
- **คำอธิบาย**: คู่มือการ build .exe (ภาษาไทย)
- **เนื้อหา**:
  - ขั้นตอนการ build สำหรับ developer
  - ขั้นตอนการใช้งานสำหรับ end user
  - การแก้ปัญหาที่พบบ่อย

#### .gitignore
- **คำอธิบาย**: รายชื่อไฟล์/โฟลเดอร์ที่ไม่ต้องการให้เข้า Git
- **ไฟล์ที่ ignore**:
  - `__pycache__/` - Python cache
  - `build/`, `dist/` - Build artifacts
  - `reports/` - Generated reports
  - `*.pyc` - Compiled Python files

## โครงสร้างโฟลเดอร์ที่สมบูรณ์

```
AirQualityReview_Project/
│
├── app.py                      # ✅ ต้องมี - Main application
├── analysis_logic.py           # ✅ ต้องมี - Analysis module
├── audit_trail.py              # ✅ ต้องมี - GAMP 5 Secure Audit Trail logic
├── agent_module.py             # ❌ ถูกลบ - AI module (removed)
├── AQR_Dashboard_v1.1.0_Fix.spec # ✅ ต้องมี - PyInstaller config
├── requirements.txt            # ✅ ต้องมี - Dependencies
├── README.md                   # ✅ แนะนำ - Documentation
├── BUILD_INSTRUCTIONS.md       # ✅ แนะนำ - Build guide
├── PROJECT_STRUCTURE.md        # ✅ แนะนำ - This file
├── .gitignore                  # ✅ แนะนำ - Git ignore
│
├── templates/                  # ✅ ต้องมี - HTML templates
│   ├── aqr.html
│   ├── transform.html
│   ├── audit_trail.html       # ✅ ต้องมี - Audit Trail Dashboard page
│   ├── ai_review.html         # ❌ ถูกลบ - AI Review page (removed)
│   └── index.html
│
├── static/                     # ✅ ต้องมี - CSS & JS
│   ├── style.css
│   └── script.js
│
├── logs/                       # ✅ ต้องมี - GxP Secure Log Directory
│   └── audit_trail.log        # 🔒 ตารางบันทึก Audit Trail เข้ารหัส Hash-Chained
│
└── data/                       # ✅ ต้องมี - Data files
    ├── SetPointLimit.xlsx
    └── [CSV files...]
```

## ขั้นตอนการ Build สรุป

1. **ติดตั้ง Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Build .exe**:
   ```bash
   pyinstaller AQR_Dashboard_v1.1.0_Fix.spec
   ```
   หรือ
   ```bash
   pyinstaller --onefile --windowed --add-data "templates;templates" --add-data "static;static" --add-data "data;data" app.py
   ```

3. **ไฟล์ Output**:
   - `dist/AQR_Dashboard_v1.1.0_Fix.exe` - ไฟล์ .exe ที่สร้างเสร็จ

## การตรวจสอบก่อน Build

- [ ] มีไฟล์ `app.py`, `analysis_logic.py`
- [ ] AI module (agent_module.py) ถูกลบออกแล้ว
- [ ] มีโฟลเดอร์ `templates/`, `static/`, `data/`
- [ ] มีไฟล์ `AQR_Dashboard_v1.1.0_Fix.spec`
- [ ] มีไฟล์ `requirements.txt` (ไม่มี AI dependencies)
- [ ] ติดตั้ง dependencies ครบถ้วน
- [ ] ทดสอบรัน `python app.py` ได้สำเร็จ

## ข้อควรระวัง

1. **Data Folders**: ต้องระบุใน PyInstaller command หรือ spec file
2. **Dependencies**: ต้องติดตั้งครบก่อน build
3. **Python Version**: ใช้ Python 3.7 ขึ้นไป
4. **Testing**: ทดสอบ .exe บนเครื่องที่ไม่มี Python ติดตั้ง
