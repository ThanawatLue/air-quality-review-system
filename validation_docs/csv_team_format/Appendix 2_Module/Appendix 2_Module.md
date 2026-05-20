# Appendix 2: Module Testing

| Document Control Information | Details |
|------------------------------|---------|
| **Project/System Name**      | Air Quality Review System (AQR) |
| **System Identifier**        | AQR-SYS-01 |
| **Document Version**         | 1.1.0 |

---

SECTION 1: OBJECTIVE
This document defines the functional specification and testing methodology for the core software modules of the Air Quality Review (AQR) System. The objective is to verify that the fundamental building blocks of the software (such as binary integrity, folder initialization, and core calculation logic) operate correctly in isolation before they are integrated into the full system workflow.

SECTION 2: PROCEDURE
1.	Execute test scenarios to simulate the system’s module-level functionality.
2.	Documentation: Record all functional outcomes in the Test Result section to confirm the integrity of the developed features.
3.	Reporting: Summarize the testing status and any deviations encountered.

SECTION 3: GENERAL DOCUMENTS
3.1 Attachment 1: Signature List
All personnel involved in the recording, reviewing, and verifying of testing documentation are required to provide their signatures in Attachment 1.
3.2 Attachment 2: Work Instruction Verification
Specify the details of the Work Instructions (WI) or User Manuals associated with the testing process.
3.3 Protocol Correction
Any planned or unplanned deviations from the testing steps or Acceptance Criteria must be documented.
3.4 Attachment 5: User Comments and Enhancement Requests Record
Any recommendations from Validation/QA identified during testing shall be recorded.
3.5 Attachment 6: System Error Record
In the event of system errors caused by infrastructure or code bugs, findings must be documented.

SECTION 4: RESPONSIBILITY
| Actions | Responsibilities |
|---------|------------------|
| Perform Testing | Coding Specialist / IT Developer |
| Review Results | CSV Specialist & GMP Specialist |
| Approve Results | Project Manager / System Owner |

SECTION 5: TEST CASE SELECTION PROCEDURE
The test selection for Module Testing is based on the Functional Risk Assessment (FRA) and the Design Specification (DS). Tests are selected to verify the exact mathematical logic (e.g., temporal alignment) and structural integrity (e.g., SHA-256 hashes) that cannot be easily verified through the user interface alone.

SECTION 6: TEST RESULT

1.	CRR-TC-01: User Identity Capture Verification
Objective:
To verify that the system securely and accurately captures the actual Windows username of the person running the application. This ensures that the Audit Trail history is always linked to a real person.
Procedure:
•	Source Code Navigation:
	Open the project repository in a code editor (e.g., VS Code).
	Navigate to the file `audit_trail.py`.
•	Logic Verification:
	Locate the `log_event` function definition.
	Verify that the system is programmed to ask Windows for the current user (`getpass.getuser()`).
Acceptance Criteria:
•	The code explicitly imports and utilizes the correct module to securely identify the user.
Results:

2.	CRR-TC-02: Temporal Alignment Logic Verification
Objective:
To verify that the system aligns time-stamps properly when comparing pressure between two rooms, allowing a small 60-second window (tolerance) to account for slight delays in different sensors sending their data.
Procedure:
•	Source Code Navigation:
	Open the project repository in a code editor.
	Navigate to the file `analysis_logic.py`.
•	Logic Verification:
	Locate the `check_reverse_violations` and `analyze_files` functions.
	Find the data joining function (`pd.merge_asof`) used for pressure corridor comparisons.
	Verify that the system is instructed to find the "nearest" time within a strict 60-second maximum limit (`tolerance=pd.Timedelta('60s')`).
Acceptance Criteria:
•	The code utilizes the "nearest" direction rule to handle minor sensor timing issues (sensor jitter).
•	The time limit is strictly set to 60 seconds to prevent the system from comparing pressure data from completely different times.
Results:

3.	IQ-TC-01: Binary Integrity & Versioning Verification
Objective:
To verify that the delivered program (`AirQualityReview.exe`) is correctly installed, matches the officially validated software build, and contains the correct version information.
Procedure:
•	System Installation:
	Locate the source installation package (the standalone program).
	Copy the `AirQualityReview.exe` file and its associated data folders to your local computer drive (e.g., `C:\AQR_System\`).
•	Navigation and Metadata Verification:
	Open Windows File Explorer.
	Navigate to the directory where you copied the application.
	Right-click on the file `AirQualityReview.exe`.
	Select 'Properties' from the menu and navigate to the 'Details' tab.
	Verify the "Product Version" field.
•	Command-Line Integrity Check (SHA-256 Checksum):
	Press the `Windows + R` keys to open the 'Run' dialog box.
	Type `powershell` and press Enter.
	In the PowerShell window, type: `cd C:\AQR_System\` (or your actual path).
	Type the command: `Get-FileHash .\AirQualityReview.exe -Algorithm SHA256 | Format-List`
•	Comparison:
	Compare the digital fingerprint (Hash value) displayed on your screen against the Master Build Record.
Acceptance Criteria:
•	Product Version explicitly displays "v1.1.0".
•	The generated SHA-256 hash perfectly matches the Master Build Record: `D12E959AC43FC8E69CC04C64ED1BFFFBFFE71EDE2CEDCB976A320DD6A113023E`
Results:

4.	IQ-TC-02: Directory Structure Verification
Objective:
To verify that the system successfully sets up its own working environment by automatically creating the necessary folders and the core security log file the first time you run it.
Procedure:
•	Initial Execution:
	Navigate to the application root directory (e.g., `C:\AQR_System\`).
	Double-click `AirQualityReview.exe` to launch the application for the first time.
	Wait for the visual dashboard (Graphical User Interface) to appear.
•	System Shutdown:
	Close the application browser window and stop the program if necessary.
•	Visual Inspection:
	Using Windows File Explorer, inspect the contents of the application root directory.
	Verify that the system has newly created two folders: `./reports` and `./logs`.
•	File Verification:
	Enter the `./logs` folder.
	Verify the presence of the `audit_trail.log` file.
Acceptance Criteria:
•	The `./reports` folder is automatically generated and present.
•	The `./logs` folder is automatically generated and present.
•	The `audit_trail.log` file is successfully initialized and located securely within the `./logs` directory.
Results:

5.	IQ-TC-04: Automated Folder Initialization
Objective:
To verify the system's ability to "self-heal". If critical folders are accidentally deleted by a user, the system must be able to automatically recreate them to prevent crashing.
Procedure:
•	Environment Preparation:
	Navigate to the application root directory.
	Ensure the application (`AirQualityReview.exe`) is completely closed.
•	Simulation of Missing Components:
	Select the `./logs` folder and delete it entirely.
	Select the `./reports` folder and delete it entirely.
	Confirm both folders are removed from the root directory.
•	System Re-initialization:
	Double-click `AirQualityReview.exe` to launch the application.
	Observe the startup process to ensure no error messages appear.
•	Verification of Self-Healing:
	Switch back to Windows File Explorer and inspect the root directory.
Acceptance Criteria:
•	The application launches successfully without displaying any system errors.
•	The system automatically re-creates the missing `./logs` and `./reports` folders to restore functionality.
Results:

6.	IQ-TC-06: Pre-Flight Integrity Check Failure
Objective:
To verify that the system has a robust self-protection mechanism. It must prevent the program from opening if it detects that the security history file (`audit_trail.log`) has been manually altered, ensuring compliance with strict data security rules (21 CFR Part 11).
Procedure:
•	Preparation:
	Navigate to the `./logs` directory.
	Right-click the `audit_trail.log` file and select 'Open with Notepad'.
•	Simulation of Unauthorized Modification (Data Tampering):
	Identify a single character or a long hash string in the text.
	Manually edit or delete characters (e.g., change a specific letter or number).
	Save the changes and close Notepad.
•	System Execution Attempt:
	Return to the root directory and double-click `AirQualityReview.exe`.
•	Verification of System Halt:
	Confirm the main visual dashboard does not open.
	Verify the exact wording of the error message displayed on the screen.
Acceptance Criteria:
•	The application must refuse to start and immediately halt all internal processes.
•	The system must display a fatal error message exactly reading: "FATAL ERROR 004: Audit Trail Integrity Check Failed".
•	Details inside the error message must mention the security violation or tampered entry.
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
•	Code Review Report (CRR)
•	Functional Specification (FS)

SECTION 9: TERMS AND DEFINITION
•	**Module Testing:** Testing individual software components or logic blocks in isolation.
•	**SHA-256:** Secure Hash Algorithm used for digital fingerprinting.

SECTION 10: ATTACHMENT
•	Attachment 1: Signature List
•	Attachment 7: Test Result Sheet
