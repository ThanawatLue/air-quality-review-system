# Appendix 3: Integration Testing

| Document Control Information | Details |
|------------------------------|---------|
| **Project/System Name**      | Air Quality Review System (AQR) |
| **System Identifier**        | AQR-SYS-01 |
| **Document Version**         | 1.1.0 |

---

SECTION 1: OBJECTIVE
This document outlines the Integration Testing methodology for the Air Quality Review (AQR) System. The objective is to verify that different components of the system (such as the User Interface, the calculation engine, and the external file system) communicate and exchange data correctly without errors.

SECTION 2: PROCEDURE
1.	Execute test scenarios focusing on data transfer between the front-end (GUI) and the back-end (Python engine).
2.	Documentation: Record all interface outcomes in the Test Result section.
3.	Reporting: Summarize the testing status and record any connection errors or data loss during transfer.

SECTION 3: GENERAL DOCUMENTS
3.1 Attachment 1: Signature List
All personnel involved must sign Attachment 1.
3.2 Attachment 2: Work Instruction Verification
Detail the Work Instructions associated with the testing process.
3.3 Protocol Correction
Any deviations must be logged.
3.4 Attachment 5: User Comments and Enhancement Requests Record
Any user comments identified during testing shall be recorded.
3.5 Attachment 6: System Error Record
Document any integration failures or infrastructure timeouts here.

SECTION 4: RESPONSIBILITY
| Actions | Responsibilities |
|---------|------------------|
| Perform Testing | Validation Engineer / IT |
| Review Results | CSV Specialist |
| Approve Results | Project Manager / System Owner |

SECTION 5: TEST CASE SELECTION PROCEDURE
Test selection for Integration Testing is based on the system boundaries defined in the Functional Specification. Tests focus on the connection between the web browser and the local server (Port 5000), as well as the system's ability to read external requirement files (`SetPointLimit.xlsx`).

SECTION 6: TEST RESULT

1.	OQ-TC-02: Limit File Dependency Verification (Missing File)
Objective:
To confirm the system blocks analysis if the configuration file (`SetPointLimit.xlsx`) is missing.
Procedure:
•	Navigate to the application root directory.
•	Temporarily move or rename `SetPointLimit.xlsx`.
•	Open the AQR application and attempt to select CSV files.
•	Observe the 'Analyze' button and error messages.
Acceptance Criteria:
•	The system displays an error message: "ERR-002: Limit File Not Found".
•	The 'Analyze' functionality is disabled.
Results:

2.	OQ-TC-03: Limit File Integrity (Invalid Data/NaN Handling)
Objective:
To verify the system handles non-numeric limit values in the Excel file without crashing.
Procedure:
•	Open `SetPointLimit.xlsx` using Microsoft Excel.
•	In the "Temperature High Limit" cell, type "NOT_A_NUMBER".
•	Save and attempt to run an analysis in the AQR application.
Acceptance Criteria:
•	The system stops the process and displays: "ERR-003: Invalid Configuration - High Limit must be a number".
Results:

3.	OQ-TC-19: Invalid CSV Header/Column Verification
Objective:
To verify that the system rejects files with incorrect or missing column headers.
Procedure:
•	Open a test CSV and modify/delete the column headers.
•	Attempt to process this file in the AQR application.
Acceptance Criteria:
•	The system displays an error: "ERR-005: Invalid File Format - Required columns not found."
Results:

4.	OQ-TC-24: Source File Traceability (SHA-256 Generation)
Objective:
To confirm that every data file (CSV) analyzed by the system creates a unique digital fingerprint in the audit log. To trust the final report, we must prove it came from a specific, original file that has not been changed. A SHA-256 hash is like a "digital fingerprint." If the file changes by even one byte, the fingerprint changes completely.
Procedure:
•	Launch the `AirQualityReview.exe` application.
•	Click the 'Select File' button and choose a valid CSV data file.
•	Click the 'Analyze' button and wait for the process to complete.
•	Navigate to the `./logs/` directory and open `audit_trail.log` with Notepad.
•	Search for the most recent entry labeled `[FILE_PROCESSED]`.
Acceptance Criteria:
•	The log entry contains the full name of the processed file.
•	The log entry contains a unique 64-character SHA-256 hash string.
Results:

5.	IQ-TC-08: Standalone Isolation Verification
Objective:
To mathematically prove that the application is fully independent. It must be capable of executing all its core functions without relying on external internet connections or pre-installed programming software (like Python) on the user's computer.
Procedure:
•	Network Isolation:
	Disable all internet and network connections on the workstation (Wi-Fi, Ethernet).
	Confirm the system is completely offline.
•	Environment Verification (No Python Installed):
	Press `Windows + R`, type `cmd`, and press Enter.
	In the Command Prompt, type `python --version` and press Enter.
	Verify that the system returns an error message stating that 'python' is not recognized.
•	Application Execution:
	Navigate to the application directory and double-click `AirQualityReview.exe`.
•	Interface Accessibility:
	Open a standard web browser (like Edge or Chrome).
	Enter the address `http://127.0.0.1:5000` in the address bar.
Acceptance Criteria:
•	The application launches successfully in a completely offline environment.
•	The visual dashboard is fully accessible and functional through the local network port.
Results:

6.	OQ-TC-23: Audit Trail Hash-Chain Tamper Detection
Objective:
To verify that the system detects unauthorized modifications to the `audit_trail.log` file and halts execution. According to regulatory rules (21 CFR Part 11), electronic records must be protected from manual changes. The system uses a "hash-chain" where each line of text is linked to the previous one mathematically. If even one letter is changed, the link breaks. This ensures that no one has edited the history of what the system did.
Procedure:
•	Open Windows File Explorer and navigate to the application root directory.
•	Enter the `./logs/` folder.
•	Right-click the `audit_trail.log` file and select 'Open with Notepad'.
•	Scroll to the end of the file, locate any long string of random characters (the "hash"), and delete or change a single character in that string.
•	Click File > Save and close Notepad.
•	Return to the application root directory and double-click `AirQualityReview.exe` to launch the application.
Acceptance Criteria:
•	The application must not open the main dashboard.
•	A popup window or console message appears with the exact text: "FATAL ERROR 004: Audit Trail Integrity Check Failed"
Results:




SECTION 7: CRITERIA FOR EVALUATION OF TEST RESULT
| Types of Test Result | Description |
|----------------------|-------------|
| Pass (P) | The test results align with the predefined expectations and requirements. |
| Conditionally Pass (CP) | The test results were inconsistent. Discrepancies have been documented for further corrective action. |
| Fail (F) | Test results fail to meet predefined criteria. Retesting is required after system correction. |
| Not Available (N/A) | Not applicable for this specific test case. |

SECTION 8: REFERENCE
•	Installation Qualification (IQ) Protocol
•	Operational Qualification (OQ) Protocol

SECTION 9: TERMS AND DEFINITION
•	**Integration Testing:** Testing the connection and data flow between two or more software modules or external systems.

SECTION 10: ATTACHMENT
•	Attachment 1: Signature List
•	Attachment 7: Test Result Sheet
