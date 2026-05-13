# Operational Qualification (OQ) Protocol: Air Quality Review System

| Document Control Information | Details |
|------------------------------|---------|
| **Project/System Name**      | Air Quality Review System (AQR) |
| **Protocol Identifier**      | OQ-AQR-01 |
| **Document Version**         | 8.0.0 (Final Executable Version) |
| **Date of Creation**         | 2026-04-29 |

---

## Change Summary & Traceability
| Test Case ID | Status | Change Description |
|--------------|--------|--------------------|
| OQ-TC-01 to OQ-TC-22 | **Expanded** | Rewritten with full step-by-step detail for non-programmers. |
| OQ-TC-23 to OQ-TC-25 | **NEW** | Added CSV format, Report Layout, and Batch processing verification. |
| OQ-TC-26 to OQ-TC-30 | **NEW** | Added Logical limits, Clock sync, User ID capture, Mixed-batch recovery, and Locale robustness. |

---

## General Instructions for Execution
1. **Required Materials:** A workstation with the AQR software installed, access to the `./logs/` and `./reports/` folders, a text editor (Notepad), and Microsoft Excel.
2. **Evidence Collection:** For every "Acceptance Criteria" check, the executor must take a screenshot and label it with the Test Case ID (e.g., `Evidence_OQ-TC-01.png`).
3. **Data Integrity:** Do not use production data for testing. Use the mock CSV files provided in the `test_data` folder.
4. **Time Synchronization:** The workstation used for testing MUST be synced to the company domain time server to ensure audit trail integrity. Manual clock changes are prohibited during execution.

---

## Section 0: Operational Definitions & Expected Outcomes
| Outcome Category | String / Indicator | Definition |
|------------------|--------------------|------------|
| **General Pass** | `Passed` (✓)       | No sustained excursions (25+ mins) detected. |
| **General Fail** | `Out of Spec` (✗)  | Sustained excursion (25+ mins) detected. |
| **Excursion Type**| `High`             | Values recorded above the Upper Limit. |
| **Excursion Type**| `Low`              | Values recorded below the Lower Limit. |
| **Pressure Status**| `over`             | Room P > Corridor P (Safe Airflow Direction). |
| **Pressure Status**| `under`            | Room P < Corridor P (Compromised Airflow). |
| **Pressure Status**| `within`           | Room P ≤ Corridor P (Total Airflow Failure). |

OPERATION QUALIFICATION (OQ)
SECTION 1: BUSINESS RULES AND LIMIT LOGIC
1.	OQ-TC-01: Business Date Adjustment (Minus 1 Day Logic)
Objective: 
To verify that the system correctly subtracts one day from the date found in the raw data filename. Many sensors save data for "Yesterday" at 00:05 AM "Today." To make sure the report shows the correct day the air was actually measured, the system must automatically move the date back by one day.
Procedure:
1.	Select the test file named `1-P050_04-06-26_00-00.csv`.
2.	Process this file using the AQR application.
3.	Open the resulting Excel report in the `./reports/` folder.
4.	Locate the cell labeled "Date of Review".
Acceptance Criteria:
The cell "Date of Review" correctly displays the value " 05 Apr 2026".

2.	OQ-TC-02: Limit File Dependency Verification (Missing File)
Objective:
To confirm the system blocks analysis if the configuration file (`SetPointLimit.xlsx`) is missing.
Procedure:
1.	Navigate to the application root directory.
2.	Right-click `SetPointLimit.xlsx` and rename it to `BACKUP_Limits.xlsx`.
3.	Open the AQR application and observe the 'Analyze' button.
Acceptance Criteria:
•	The system displays an error message: "ERR-002: Limit File Not Found".
•	The 'Analyze' functionality is disabled.

3.	OQ-TC-03: Limit File Integrity (Invalid Data/NaN Handling)
Objective: 
To verify the system handles non-numeric limit values in the Excel file without crashing.
Procedure:
1.	Open `SetPointLimit.xlsx` using Microsoft Excel.
2.	In the "Temperature High Limit" cell, delete the value and type "NOT_A_NUMBER".
3.	Save the file and attempt to run an analysis in the AQR application.
Acceptance Criteria:
The system stops the process and displays: "ERR-003: Invalid Configuration - High Limit must be a number".

SECTION 2: PARAMETER-SPECIFIC VALIDATION - TEMPERATURE
4.	OQ-TC-04: Temperature High Limit (Sustained 25-Min Excursion)
Objective:
To verify that 6 consecutive points (25 mins) above the limit trigger a failure.
Procedure:
1.	Open the AQR application.
2.	In `SetPointLimit.xlsx`, set the High Limit to 25.0°C.
3.	Select the CSV file where 6 consecutive data points at 5-minute intervals, the temperature value more than 25°C.
4.	Process the file ('Analyze' button) and check the result status.
5.	Select the CSV file with up to 5 consecutive data points at 5-minute intervals where temperature value over 25°C.
6.	Process the file ('Analyze' button) and check the result status.
Acceptance Criteria:
Result status in the report shows: `Out of Spec` (✗) and `Passed` (✓) respectively.

5.	OQ-TC-05: Temperature Continuity Rule (Data Gap Handling)
Objective:
To verify that missing data points prevent a violation from being reported.
Procedure:
1.	Open the AQR application.
2.	In `SetPointLimit.xlsx`, set the High Limit to 25.0°C.
3.	Select the data file where 3 points of temperature value more than 25°C, followed by a 10-minute gap (one point within 25°C), then 3 or more points over 25.0°C.
4.	Process the file ('Analyze' button) and check the result status.
Acceptance Criteria:
Result status in the report shows: `Passed` (✓) caused by the system correctly identifies that there was no continuous 25-minute violation.

SECTION 3: PARAMETER-SPECIFIC VALIDATION - HUMIDITY
6.	OQ-TC-06: Humidity High Limit (Sustained 25-Min Excursion)
Objective:
Confirm that sustained high humidity (above 65%) is flagged correctly.
Procedure:
1.	Open the AQR application.
2.	In `SetPointLimit.xlsx`, set the Humidity High Limit to 65.0%RH.
3.	Select the CSV file where 6 consecutive data points at 5-minute intervals, the humidity value more than 65.0%RH.
4.	Process the file ('Analyze' button) and check the result status.
5.	Select the CSV file with up to 5 consecutive data points at 5-minute intervals, where the humidity values over 65.0%RH.
6.	Process the file ('Analyze' button) and check the result status.
Acceptance Criteria:
Result status in the report shows: `Out of Spec` (✗) and `Passed` (✓) respectively.

7.	OQ-TC-07: Humidity Low Limit (Sustained 25-Min Excursion)
Objective:
Confirm that sustained low humidity (below 35%) is flagged correctly.
Procedure:
1.	Open the AQR application.
2.	In `SetPointLimit.xlsx`, set the Humidity Low Limit to 35.0%RH.
3.	Select the CSV file where 6 consecutive data points at 5-minute intervals, the humidity value below 35%RH.
4.	Process the file ('Analyze' button) and check the result status.
5.	Select the CSV file with up to 5 consecutive data points at 5-minute intervals, where the humidity values under 35%RH.
6.	Process the file ('Analyze' button) and check the result status.
Acceptance Criteria:
Result status in the report shows: `Out of Spec` (✗) and `Passed` (✓) respectively.

8.	OQ-TC-08: Humidity Continuity Rule (Data Gap Handling)
Objective:
To verify that missing data points prevent a violation from being reported.
Procedure:
1.	Open the AQR application.
2.	In `SetPointLimit.xlsx`, set the Humidity Low Limit to 65.0%RH.
3.	Select the data file with 3 points of humidity value over 65%RH, followed by a 10-minute gap (one point equal to or less than 64.9%RH), then 3 points over 65.0%RH.
4.	Process the file ('Analyze' button) and check the result status.
Acceptance Criteria:
Result status in the report shows: `Passed` (✓) caused by the system correctly identifies that there was no continuous 25-minute violation.

9.	OQ-TC-09: Humidity Separating Low/High Limit Rule
Objective:
To verify that the system can detect the separate low/high out of the limit and reporting in the separating format.
Procedure:
1.	Open the AQR application.
2.	In `SetPointLimit.xlsx`, set the Humidity Low Limit to 35.0%RH and Humidity High Limit to 65%RH.
3.	Select the data file where at least 6 consecutive points, the humidity value are over 65.0%RH, followed by 6 or more consecutive points which the humidity value below 35%RH.
4.	Process the file ('Analyze' button) and check the result status.
Acceptance Criteria:
Result status in the report shows: `Out of Spec` (✗) followed by detailed separating interval that relative humidity out of low limit and high limit.

SECTION 4: PARAMETER-SPECIFIC VALIDATION - PRESSURE
10.	OQ-TC-10: Pressure Corridor Check: 'within' status (For Room Pressure Setpoint 15 and 30 Pa)
Objective: 
Verify that the system flags a room when its pressure is lower than the corridor pressure.
Procedure:
1.	Open the AQR application.
2.	In `SetPointLimit.xlsx`, set the Pressure Low Limit, Pressure High Limit, and Room Pressure Comparison as per expected room pressure condition.
3.	Select data where room pressure value is over or under the room Pressure High or Low Limit for 6 consecutive respectively, but less than corridor pressure value at the same timestamp.
4.	Process the file ('Analyze' button) and check the result status.
Acceptance Criteria:
Result status in the report shows: `Passed` (✓) and status string shows: `within` Corridor.

11.	 OQ-TC-11: Pressure Corridor Check: 'over' status (For Room Pressure Setpoint 15 and 30 Pa)
Objective:
Verify that if a room is over its own internal limit and above the corridor, it is flagged as 'over'.
Procedure:
1.	Open the AQR application.
2.	In `SetPointLimit.xlsx`, set the Pressure Low Limit, Pressure High Limit, and Room Pressure Comparison as per expected room pressure condition.
3.	Select data where room pressure value is over or under the room Pressure High or Low Limit for 6 consecutive respectively, and over corridor pressure value at the same timestamp.
4.	Process the file ('Analyze' button) and check the result status.
Acceptance Criteria:
Result status in the report shows: `Out of Spec` (✗) and status string shows: `over` Corridor.

12.	OQ-TC-12: Pressure Corridor Check: 'within' status (For Room Pressure Setpoint 45 Pa)
Objective: 
Verify that the system flags a room when its pressure is higher than the corridor pressure.
Procedure:
1.	Open the AQR application.
2.	In `SetPointLimit.xlsx`, set the Pressure Low Limit, Pressure High Limit, and Room Pressure Comparison as per expected room pressure condition.
3.	Select data where room pressure value is over or under the room Pressure High or Low Limit for 6 consecutive respectively, but more than corridor pressure value at the same timestamp.
4.	Process the file ('Analyze' button) and check the result status.
Acceptance Criteria:
Result status in the report shows: `Passed` (✓) and status string shows: `over` Corridor.

13.	 OQ-TC-13: Pressure Corridor Check: 'under' status (For Room Pressure Setpoint 45 Pa)
Objective:
Verify that if a room is over its own internal limit and below the corridor, it is flagged as 'under'.
Procedure:
1.	Open the AQR application.
2.	In `SetPointLimit.xlsx`, set the Pressure Low Limit, Pressure High Limit, and Room Pressure Comparison as per expected room pressure condition.
3.	Select data where room pressure value is over or under the room Pressure High or Low Limit for 6 consecutive respectively, and under corridor pressure value at the same timestamp.
4.	Process the file ('Analyze' button) and check the result status.
Acceptance Criteria:
Result status in the report shows: `Out of Spec` (✗) and status string shows: `under` Corridor.

SECTION 5: UI AND DATA TRANSFORMATION
14.	OQ-TC-14: UI Transformation: Main Plant, Module 5, and Pilot Splitter Logic
Objective:
To verify that the system can split a bulk Main Plant (RMT, RMH, and RPT), Module 5, Pilot scale files into individual room CSVs.
Procedure:
1.	Open the AQR application.
2.	Navigate to Data Transformation module in the left sidebar.
3.	Upload a bulk CSV file containing data for different rooms.
4.	Click the 'Split Report' button in the AQR application.
5.	Navigate to the generated output folder.
Acceptance Criteria:
•	A new folder has been created with a timestamped name.
•	The folder contains individual CSV files, one for each room for number equal to bulk CSV file.

15.	OQ-TC-15: UI Filter: Date Range Selection Accuracy
Objective:
To ensure the report only contains data points within the selected date range.
Procedure:
1.	Open the AQR application.
2.	Select the `SetPointLimit.xlsx` and CSV files for 01 Mar 2026 to 10 Mar 2026.
3.	Set the UI date filter to start on 01-Mar and end on 05-Mar.
4.	Process a dataset containing data for the entire month of March.
Acceptance Criteria:
The final Excel report only displays rows with timestamps from March 1st to March 5th.

16.	OQ-TC-16: UI Filter: Room/Location Exclusion Logic
Objective:
Verify the system can ignore specific rooms if they are not selected in the checklist.
Procedure:
1.	Open the AQR application.
2.	Select the `SetPointLimit.xlsx` and CSV files for at least Module 1 and other room CSV files.
3.	In the AQR UI Room List, uncheck the box for "Module 1".
4.	Run the analysis for the whole building.
Acceptance Criteria:
The final Excel report does not contain any data or sheets for Module 1.
 

SECTION 6: ROBUSTNESS AND FINAL REPORTING
17.	OQ-TC-17: Robustness: Corrupt Data Value Handling (Non-numeric data)
Objective:
Verify that the system skips "garbage" data (like "Data Loss" or "No Data") without crashing.
Procedure:
1.	Open the AQR application.
2.	Select the `SetPointLimit.xlsx` and CSV files for at non-numeric data CSV files.
3.	Process the file ('Analyze' button) and check the result status.
Acceptance Criteria:
•	The system completes the analysis without errors.
•	Result status in the report shows: `Data Loss` and period of its.
•	A "Warning" entry regarding the non-numeric data is recorded in `audit_trail.log`.

18.	OQ-TC-18: System Versioning and Report Metadata Traceability
Objective: 
To ensure the final report proves which version of the software was used.
Procedure:
1.	Generate any standard report and open the Excel file.
2.	Look for the "Software Version" and "Generation Date" fields.
Acceptance Criteria:
The software version (e.g., v1.1.0) is clearly printed on the report.

SECTION 7: FORMATTING AND BATCH PROCESSING
19.	 OQ-TC-19: Invalid CSV Header/Column Verification
Objective:
To verify that the system rejects files with incorrect or missing column headers.
Procedure:
1.	Select a CSV file and change the header "Temperature" to "Temp_Value".
2.	Attempt to process this file in the AQR application.
Acceptance Criteria:
The system displays an error: "ERR-005: Invalid File Format - Required columns not found."

SECTION 8: ADVANCED ROBUSTNESS AND DATA INTEGRITY
20.	OQ-TC-20: Logical Limit Constraint Validation
Objective:
To prevent the entry of logically impossible limits (e.g., High Limit < Low Limit).
Procedure:
1.	Open `SetPointLimit.xlsx` and set Humidity High Limit to 35%RH and Low Limit to 65%RH.
2.	Save and attempt to run an analysis.
Acceptance Criteria:
The system displays: "ERR-006: Configuration Error - High Limit cannot be lower than Low Limit."

21.	OQ-TC-21: System Clock & Timestamp Synchronization
Objective:
To verify that audit logs match the local workstation system clock.
Procedure:
1.	Note the current Windows System Time.
2.	Perform an action in the AQR application.
3.	Check the timestamp of that action in `audit_trail.log`.
Acceptance Criteria:
The log timestamp matches the Windows clock.

22.	 OQ-TC-22: User Identity Capture (OS-Level Traceability)
Objective:
To verify that the system identifies the Windows User account performing the actions.
Procedure:
1.	Open `audit_trail.log` and inspect the "User" field of the last entry.
Acceptance Criteria:
The "User" field exactly matches the currently logged-in Windows Username.


SECTION 8: SYSTEM SECURITY AND FILE INTEGRITY (ยกไปไว้เป็น section test สุดท้าย)
23.	OQ-TC-23: Audit Trail Hash-Chain Tamper Detection
Objective:
To verify that the system detects unauthorized modifications to the `audit_trail.log` file and halts execution. According to regulatory rules (21 CFR Part 11), electronic records must be protected from manual changes. The system uses a "hash-chain" where each line of text is linked to the previous one mathematically. If even one letter is changed, the link breaks. This ensures that no one has edited the history of what the system did.
Procedure:
1.	Open Windows File Explorer and navigate to the application root directory.
2.	Enter the `./logs/` folder.
3.	Right-click the `audit_trail.log` file and select 'Open with Notepad'.
4.	Scroll to the end of the file, locate any long string of random characters (the "hash"), and delete or change a single character in that string.
5.	Click File > Save and close Notepad.
6.	Return to the application root directory and double-click `AirQualityReview.exe` to launch the application.
Acceptance Criteria:
•	The application must not open the main dashboard.
•	A popup window or console message appears with the exact text: "FATAL ERROR 004: Audit Trail Integrity Check Failed"

24.	OQ-TC-24: Source File Traceability (SHA-256 Generation)
Objective:
To confirm that every data file (CSV) analyzed by the system creates a unique digital fingerprint in the audit log. To trust the final report, we must prove it came from a specific, original file that has not been changed. A SHA-256 hash is like a "digital fingerprint." If the file changes by even one byte, the fingerprint changes completely.
Procedure:
1.	Launch the `AirQualityReview.exe` application.
2.	Click the 'Select File' button and choose a valid CSV data file (e.g., `SampleData.csv`).
3.	Click the 'Analyze' button and wait for the process to complete.
4.	Navigate to the `./logs/` directory and open `audit_trail.log` with Notepad.
5.	Search for the most recent entry labeled `[FILE_PROCESSED]`.
Acceptance Criteria:
•	The log entry contains the full name of the processed file.
•	The log entry contains a unique 64-character SHA-256 hash string.
 
25.	OQ-TC-25: Audit Trail Missing File Handling
Objective:
To ensure the system refuses to run if the audit trail file is deleted. If the history of the system's actions is missing, the system cannot be considered "validated" or "secure." Deleting the log file is a common way to hide unauthorized actions, so the system must prevent this.
Procedure:
1.	Ensure the AQR application is completely closed.
2.	Open Windows File Explorer and navigate to the `./logs/` directory.
3.	Select the `audit_trail.log` file and press the `Delete` key.
4.	Attempt to launch `AirQualityReview.exe`.
Acceptance Criteria:
•	The application fails to launch the main processing interface.
•	The system automatically creates a new, empty `audit_trail.log` file.
