# Build Instructions — Air Quality Review System

---

## สำหรับผู้พัฒนา (Developer)

### ขั้นตอนการสร้างไฟล์ .exe

#### 1. ตรวจสอบการติดตั้ง Python และ pip

```bash
python --version   # ต้องการ 3.7 ขึ้นไป
pip --version
```

#### 2. ติดตั้ง Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies หลัก:**

| Package | ใช้ทำอะไร |
|---------|-----------|
| `flask` | Web framework |
| `waitress` | Production WSGI server (SSE-compatible, threads=8) |
| `pandas` | Data processing |
| `openpyxl` / `xlsxwriter` | Excel read/write |
| `pyinstaller` | Build tool |

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
pyinstaller --onefile --windowed --version-file=app_version_info.txt ^
  --add-data "templates;templates" ^
  --add-data "static;static" ^
  --add-data "data;data" app.py
```

**คำอธิบายพารามิเตอร์:**

| พารามิเตอร์ | ความหมาย |
|------------|----------|
| `--onefile` | รวมทุกอย่างไว้ในไฟล์ .exe ไฟล์เดียว |
| `--windowed` | รันโดยไม่มีหน้าต่าง console (GUI mode) |
| `--version-file` | ใส่ข้อมูล version ใน Windows properties |
| `--add-data "templates;templates"` | รวมโฟลเดอร์ templates (จำเป็นสำหรับ Flask) |
| `--add-data "static;static"` | รวมโฟลเดอร์ static (CSS, JS) |
| `--add-data "data;data"` | รวมโฟลเดอร์ data (SetPointLimit files) |

#### 5. ไฟล์ที่ได้

```
dist/
└── app.exe     ← ไฟล์ที่แจกจ่ายให้ผู้ใช้
```

#### 6. ทดสอบก่อนแจกจ่าย

1. สร้างโฟลเดอร์ใหม่ที่สะอาด (ไม่ใช่โฟลเดอร์โปรเจกต์)
2. คัดลอก `app.exe` ไปไว้ในโฟลเดอร์นั้น
3. สร้างโฟลเดอร์ `reports/` ในตำแหน่งเดียวกัน
4. รันบนคอมพิวเตอร์ที่ **ไม่มี Python ติดตั้ง** เพื่อยืนยันว่า standalone ได้จริง

---

## สำหรับผู้ใช้งาน (End User)

### การเตรียมคอมพิวเตอร์

#### 1. ติดตั้ง Microsoft Visual C++ Redistributable (จำเป็น)

- ข้อผิดพลาด `Failed to load Python DLL` เกิดจากไม่มีส่วนประกอบนี้
- ดาวน์โหลด: https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170
- เลือก x64 version
- ติดตั้งและรีสตาร์ทคอมพิวเตอร์

#### 2. เตรียมโฟลเดอร์

```
AirQualityReview/
├── app.exe
└── reports/        ← โฟลเดอร์ว่างเปล่า — ต้องสร้างก่อนรันแอป
```

> หากไม่มีโฟลเดอร์ `reports/` แอปจะสร้างให้อัตโนมัติ แต่แนะนำให้สร้างล่วงหน้า

#### 3. รันแอปพลิเคชัน

- ดับเบิลคลิกที่ `app.exe`
- รอ 5–15 วินาที (ระยะ unpack + server startup)
- เบราว์เซอร์จะเปิดขึ้นอัตโนมัติที่ `http://127.0.0.1:5000/aqr`

#### 4. การใช้งานเบื้องต้น

1. เลือก **Phase I** หรือ **Phase II** ตามแหล่งข้อมูล
2. กด **Browse** เพื่อเลือกโฟลเดอร์ CSV และไฟล์ SetPointLimit.xlsx
3. กำหนดช่วงวันที่ แล้วกด **Scan & Load Available Rooms**
4. เลือกห้องที่ต้องการวิเคราะห์
5. กด **Generate Summary Reports** — log จะขึ้นแบบ real-time ระหว่างประมวลผล
6. หลัง analysis เสร็จ กด **Download AQR Program Report** เพื่อดาวน์โหลด Excel
7. กด **Generate Visual Graphs** เพื่อดูกราฟ (ปุ่มจะเปิดใช้งานได้หลัง analysis เสร็จเท่านั้น)

---

## การทำงานของ Server (ข้อมูลเพิ่มเติมสำหรับนักพัฒนา)

### Development Mode (`python app.py`)
- ใช้ Flask built-in server พร้อม `debug=True`
- SSE streaming ทำงานได้ทันที
- Auto-reload เมื่อแก้ไขไฟล์

### Production Mode (`.exe`)
- ใช้ Waitress WSGI server
- Config: `threads=8, channel_timeout=3600`
- `threads=8` จำเป็นเพราะ SSE connection ครอง 1 thread ตลอดช่วงที่ analysis ทำงาน
- `channel_timeout=3600` รองรับ analysis ที่ใช้เวลานานถึง 1 ชั่วโมง
- ทำงานที่ `http://127.0.0.1:5000` (localhost เท่านั้น ตาม IQ-TC-06)

### SSE Streaming Architecture
- `POST /analyze` → return `job_id` ทันที + spawn background thread
- `GET /stream/<job_id>` → SSE connection ส่ง log ทีละบรรทัด
- `GET /plot/<job_id>` → fetch chart data แยก (lazy loading)
- มี `_analysis_lock` ป้องกัน concurrent analysis (1 ครั้งต่อเวลา)

---

## ไฟล์ที่จำเป็นสำหรับการ Build

### Source Code (ต้องมีทุกไฟล์)

```
app.py                   ← Main Flask application
analysis_logic.py        ← Core analysis engine
audit_trail.py           ← GAMP 5 audit trail
app.spec                 ← PyInstaller spec
app_version_info.txt     ← Windows version metadata
requirements.txt         ← Python dependencies
templates/               ← HTML templates (aqr.html, transform.html)
static/                  ← CSS + JavaScript
data/                    ← SetPointLimit.xlsx, SetPointLimit_Phase2.xlsx
```

### ไฟล์ที่ไม่ต้องรวมใน Build

```
reports/          ← สร้างใหม่บนเครื่องผู้ใช้
logs/             ← สร้างใหม่บนเครื่องผู้ใช้
dist/             ← output จาก PyInstaller
build/            ← temp จาก PyInstaller
__pycache__/      ← Python cache
validation_docs/  ← เอกสาร (ไม่จำเป็นสำหรับ runtime)
data/C/           ← sample data (optional — ขึ้นอยู่กับ spec)
```

---

## การแก้ปัญหา (Troubleshooting)

### ปัญหา: Failed to load Python DLL
**สาเหตุ:** ไม่มี Microsoft Visual C++ Redistributable  
**วิธีแก้:** ติดตั้ง VC++ Redistributable x64

### ปัญหา: แอปไม่เปิดขึ้น / เปิดแล้วปิดเลย
**สาเหตุ:** โฟลเดอร์ `reports/` ไม่มี หรือ port 5000 ถูกใช้งานอยู่  
**วิธีแก้:**
- สร้างโฟลเดอร์ `reports/` ในตำแหน่งเดียวกับ .exe
- ตรวจสอบว่า port 5000 ว่าง: `netstat -ano | findstr :5000`
- ลองรันในโหมด Administrator

### ปัญหา: หน้าเว็บโหลดแล้ว log ไม่ขึ้น / ค้างระหว่าง analysis
**สาเหตุ:** SSE connection หลุด หรือ browser บล็อก EventSource  
**วิธีแก้:**
- ตรวจสอบ browser console (F12) สำหรับ SSE errors
- ตรวจสอบว่า antivirus/firewall ไม่บล็อก localhost
- รีโหลดหน้า (F5) แล้วลองใหม่

### ปัญหา: ปุ่ม Generate Visual Graphs กดไม่ได้
**สาเหตุ:** ยังไม่ได้รัน analysis หรือ analysis ล้มเหลว  
**วิธีแก้:** รัน Generate Summary Reports ให้เสร็จก่อน — ปุ่มจะเปิดอัตโนมัติเมื่อ analysis สำเร็จ

### ปัญหา: "Another analysis is already running"
**สาเหตุ:** กด Analyze ซ้ำขณะที่ยัง process อยู่  
**วิธีแก้:** รอให้ analysis ปัจจุบันเสร็จก่อน (ดู log ที่ขึ้น real-time)

### ปัญหา: ห้อง Phase II ไม่ขึ้นใน room list
**สาเหตุ:** ไม่พบไฟล์ `_RMT_` ในโครงสร้างโฟลเดอร์  
**วิธีแก้:**
- ตรวจสอบว่าโฟลเดอร์มีไฟล์ที่มี `_RMT_` ในชื่อ
- ตรวจสอบ room ID ในชื่อไฟล์ตรงกับ `SetPointLimit_Phase2.xlsx`

---

## Version History

| Version | ความเปลี่ยนแปลงหลัก |
|---------|---------------------|
| v1.1.0 | Phase II (EMS) support, SSE real-time streaming, background thread analysis, lazy chart loading, violation log shows full rows with limit values in headers, `requestAnimationFrame` DOM batching |
| v1.0.x | Phase I (BAS) only, synchronous analysis, single JSON response |
