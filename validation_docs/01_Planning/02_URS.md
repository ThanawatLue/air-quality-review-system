# User Requirements Specification (URS): Air Quality Review System

| Document Control Information | Details |
|------------------------------|---------|
| **Project/System Name**      | Air Quality Review System (AQR) |
| **System Identifier**        | AQR-SYS-01 |
| **Document Version**         | 1.1.0 (Data Transformation & Strict Continuity Edition) |
| **Date of Creation**         | 2026-04-23 |

---

SECTION 1: INTRODUCTION
This document outlines the complete business, operational, functional, and security requirements for the Air Quality Review (AQR) System. The system is delivered as a Standalone Executable (`AQR_Dashboard_v1.1.0.exe`). This means it is packaged as a single, ready-to-use file that contains all complex calculation logic and data security controls, ensuring it runs consistently on any computer without needing extra software installation.

SECTION 2: OPERATIONAL & WORKFLOW REQUIREMENTS

| Req. ID | Requirement Description | Priority |
|---------|-------------------------|----------|
| **UR-OP-01** | The system shall be delivered as a single standalone program (`AQR_Dashboard_v1.1.0.exe`). This avoids compatibility issues and removes the need for users to install programming tools (like Python) on their computers. | High |
| **UR-OP-02** | The system shall provide a web-based Graphical User Interface (GUI). This interface will include an 'Analysis' screen for generating reports and a 'Data Transformation' screen for splitting large files. | High |
| **UR-OP-03** | The user interface shall allow users to browse and select files directly from network folders or local drives. This internal file browser must bypass standard internet browser security limits that usually block access to local files. | High |
| **UR-OP-04** | The user interface shall include a calendar widget to let users easily select the 'Start Date' and 'End Date' for their reports. | High |
| **UR-OP-05** | The system shall read the acceptable environmental limits (like max temperature) from an external Excel file named `SetPointLimit.xlsx`. This file must be kept in the same folder as the main application. | High |
| **UR-OP-06** | The system shall generate the final summary report in Microsoft Excel (.xlsx) format so it is easy to read. It shall also export transformed data in standard CSV format for further use. | High |

SECTION 3: FUNCTIONAL & CALCULATION REQUIREMENTS (EMBEDDED LOGIC)

| Req. ID | Requirement Description | Priority |
|---------|-------------------------|----------|
| **UR-FN-01** | **Header Parsing:** The system shall automatically find where the actual data starts in a messy CSV file by searching for the specific word `<>Date`. | High |
| **UR-FN-02** | **Point Mapping:** The system shall automatically identify which column belongs to Temperature, Humidity, or Pressure by matching the Room ID with the column descriptions provided in the file. | High |
| **UR-FN-03** | **25-Minute Rule (Strict Continuity):** The system shall flag an event as a "Violation" ONLY IF the temperature or humidity stays outside the acceptable limits for a continuous 25 minutes. The system will verify this by checking exactly 6 consecutive data points recorded at 5-minute intervals. | High |
| **UR-FN-04** | **Data Gap Handling:** If there is missing data or a time gap larger than 10 minutes between records, the system must break the continuity and reset the 25-minute violation counter. | High |
| **UR-FN-05** | **Pressure Synchronization:** When comparing the air pressure of a room against a corridor, the system must strictly match the data by the exact time it was recorded to prevent false alarms caused by delayed sensor readings. | High |
| **UR-FN-06** | **Statistical Summaries:** Whenever the system detects a 25-minute violation, the final report must show the lowest (Minimum) and highest (Maximum) values recorded during that specific incident. | High |
| **UR-FN-07** | **Deduplication:** The system must automatically detect and remove duplicated data rows (for example, if the system accidentally recorded the same room twice at the exact same second) before analyzing the data. | High |
| **UR-FN-08** | **Software Versioning Display:** To prove which version of the software generated the report, the system must display its version number (e.g., v1.1.0) on the screen and permanently write it into the top corner of every generated Excel report. | High |
| **UR-FN-09** | **Data Transformation:** The system shall provide a tool to split massive, combined data files (like entire plant reports) into separate, smaller files for each specific room. It must be smart enough to recognize different room naming conventions used by the sensors. | High |

SECTION 4: DATA INTEGRITY & SECURITY REQUIREMENTS (21 CFR PART 11)

| Req. ID | Requirement Description | Priority |
|---------|-------------------------|----------|
| **UR-DI-01** | **Secure Audit Trail:** The system must automatically record a history of all important actions in a text file (`audit_trail.log`). To prevent tampering, each record must be mathematically linked to the previous one using cryptographic hashing (similar to blockchain technology). If anyone manually edits the file, the system will detect it and halt. | Critical |
| **UR-DI-02** | **Audit Trail Content:** Every entry in the history log must explicitly state the exact Time, the Windows Username of the person running the app, the Action they performed, and the final result. | Critical |
| **UR-DI-03** | **Source File Integrity Check:** The system must calculate a unique digital fingerprint (SHA-256 checksum) for every raw data file it processes. This fingerprint must be saved in the log to prove the data was never altered. | High |
| **UR-DI-04** | **Limit File Version Tracking:** Every time the system runs, it must check the `SetPointLimit.xlsx` file, record when it was last modified, and calculate its digital fingerprint to ensure the acceptable limits were not secretly changed. | High |
| **UR-DI-05** | **Non-Destructive Processing:** The system must strictly open all original data files in "Read-Only" mode. The software must physically lack the ability to delete or modify the original source data. | Critical |
| **UR-DI-06** | **Error Exception Modals:** If the system encounters a critical error, it must completely stop processing and show a clear error message pop-up on the screen, rather than hiding the error and producing an incorrect report. | High |
| **UR-DI-07** | **Data Backup Compatibility:** The folders where the system saves its reports and logs must be fully compatible with the IT department's automated daily backup software. | High |
| **UR-DI-08** | **Binary Integrity Verification:** The main application file (`AQR_Dashboard_v1.1.0.exe`) must have a verifiable digital fingerprint that matches the official record from the developers, proving it is the authentic, uninfected software. | Critical |

SECTION 5: REPORTING & OUTPUT FORMATTING REQUIREMENTS

| Req. ID | Requirement Description | Priority |
|---------|-------------------------|----------|
| **UR-RP-01** | The generated Excel report shall include organized columns for 'Room no.', 'Room name', 'Specification' (the limits used), and 'Analysis results'. | High |
| **UR-RP-02** | The Excel report shall organize the data by date, using a visually clear merged row to separate each new day. | Medium |
| **UR-RP-03** | In the 'Analysis results' column, the system shall clearly print "Passed" if no sustained 25-minute violations occurred. | High |
| **UR-RP-04** | If a violation does occur, the report must clearly list the exact Start Time and End Time of the problem. | High |
| **UR-RP-05** | To ensure the report is professional and readable, it shall be formatted using 'Times New Roman' font, size 11, with text centered in the cells. | Low |

---
**Document Approval Signatures**
(To be signed upon finalization)
