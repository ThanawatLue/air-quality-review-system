# Installation Qualification (IQ) Protocol: Air Quality Review System

| Document Control Information | Details |
|------------------------------|---------|
| **Project/System Name**      | Air Quality Review System (AQR) |
| **Protocol Identifier**      | IQ-AQR-01 |
| **Document Version**         | 1.1.0 (Detailed Procedure - Original Content Restored) |
| **Date of Creation**         | 2026-04-23 |

---

SECTION 1: BINARY INTEGRITY & VERSIONING VERIFICATION (REF: UR-DI-08)
1.	IQ-TC-01: Binary Integrity & Versioning Verification
Objective:
To verify that the delivered program (`AirQualityReview.exe`) is correctly installed, matches the officially validated software build, and contains the correct version information.

Procedure:
1.	System Installation:
    •	Locate the source installation package (the standalone program).
    •	Copy the `AirQualityReview.exe` file and its associated data folders to your local computer drive (e.g., `C:\AQR_System\`).
2.	Navigation and Metadata Verification:
    •	Open Windows File Explorer.
    •	Navigate to the directory where you copied the application.
    •	Right-click on the file `AirQualityReview.exe`.
    •	Select 'Properties' from the menu and navigate to the 'Details' tab.
    •	Verify the "Product Version" field.
3.	Command-Line Integrity Check (SHA-256 Checksum):
    •	Press the `Windows + R` keys to open the 'Run' dialog box.
    •	Type `powershell` and press Enter.
    •	In the PowerShell window, type: `cd C:\AQR_System\` (or your actual path).
    •	Type the command: `Get-FileHash .\AirQualityReview.exe -Algorithm SHA256 | Format-List`
4.	Comparison:
    •	Compare the digital fingerprint (Hash value) displayed on your screen against the Master Build Record.

Acceptance Criteria:
•	Product Version explicitly displays "v1.1.0".
•	The generated SHA-256 hash perfectly matches the Master Build Record: `CBFF211004AFDCB4EC4D0223796632DA936100AF4477E0FFB0547F208B7D0B07`


SECTION 2: DIRECTORY STRUCTURE VERIFICATION
2.	IQ-TC-02: Directory Structure Verification
Objective:
To verify that the system successfully sets up its own working environment by automatically creating the necessary folders and the core security log file the first time you run it.

Procedure:
1.	Initial Execution:
    •	Navigate to the application root directory (e.g., `C:\AQR_System\`).
    •	Double-click `AirQualityReview.exe` to launch the application for the first time.
    •	Wait for the visual dashboard (Graphical User Interface) to appear.
2.	System Shutdown:
    •	Close the application browser window and stop the program if necessary.
3.	Visual Inspection:
    •	Using Windows File Explorer, inspect the contents of the application root directory.
    •	Verify that the system has newly created two folders: `./reports` and `./logs`.
4.	File Verification:
    •	Enter the `./logs` folder.
    •	Verify the presence of the `audit_trail.log` file.

Acceptance Criteria:
•	The `./reports` folder is automatically generated and present.
•	The `./logs` folder is automatically generated and present.
•	The `audit_trail.log` file is successfully initialized and located securely within the `./logs` directory.


SECTION 3: AUTOMATED FOLDER INITIALIZATION (REF: CS 2.0)
3.	IQ-TC-04: Automated Folder Initialization
Objective:
To verify the system's ability to "self-heal". If critical folders are accidentally deleted by a user, the system must be able to automatically recreate them to prevent crashing.

Procedure:
1.	Environment Preparation:
    •	Navigate to the application root directory.
    •	Ensure the application (`AirQualityReview.exe`) is completely closed.
2.	Simulation of Missing Components:
    •	Select the `./logs` folder and delete it entirely.
    •	Select the `./reports` folder and delete it entirely.
    •	Confirm both folders are removed from the root directory.
3.	System Re-initialization:
    •	Double-click `AirQualityReview.exe` to launch the application.
    •	Observe the startup process to ensure no error messages appear.
4.	Verification of Self-Healing:
    •	Switch back to Windows File Explorer and inspect the root directory.

Acceptance Criteria:
•	The application launches successfully without displaying any system errors.
•	The system automatically re-creates the missing `./logs` and `./reports` folders to restore functionality.


SECTION 4: STANDALONE ISOLATION VERIFICATION
4.	IQ-TC-06: Standalone Isolation Verification
Objective:
To mathematically prove that the application is fully independent. It must be capable of executing all its core functions without relying on external internet connections or pre-installed programming software (like Python) on the user's computer.

Procedure:
1.	Network Isolation:
    •	Disable all internet and network connections on the workstation (Wi-Fi, Ethernet).
    •	Confirm the system is completely offline.
2.	Environment Verification (No Python Installed):
    •	Press `Windows + R`, type `cmd`, and press Enter.
    •	In the Command Prompt, type `python --version` and press Enter.
    •	Verify that the system returns an error message stating that 'python' is not recognized.
3.	Application Execution:
    •	Navigate to the application directory and double-click `AirQualityReview.exe`.
4.	Interface Accessibility:
    •	Open a standard web browser (like Edge or Chrome).
    •	Enter the address `http://127.0.0.1:5000` in the address bar.

Acceptance Criteria:
•	The application launches successfully in a completely offline environment.
•	The visual dashboard is fully accessible and functional through the local network port.


SECTION 5: PRE-FLIGHT INTEGRITY CHECK FAILURE (NEGATIVE TEST)
5.	IQ-TC-07: Pre-Flight Integrity Check Failure
Objective:
To verify that the system has a robust self-protection mechanism. It must prevent the program from opening if it detects that the security history file (`audit_trail.log`) has been manually altered, ensuring compliance with strict data security rules (21 CFR Part 11).

Procedure:
1.	Preparation:
    •	Navigate to the `./logs` directory.
    •	Right-click the `audit_trail.log` file and select 'Open with Notepad'.
2.	Simulation of Unauthorized Modification (Data Tampering):
    •	Identify a single character or a long hash string in the text.
    •	Manually edit or delete characters (e.g., change a specific letter or number).
    •	Save the changes and close Notepad.
3.	System Execution Attempt:
    •	Return to the root directory and double-click `AirQualityReview.exe`.
4.	Verification of System Halt:
    •	Confirm the main visual dashboard does not open.
    •	Verify the exact wording of the error message displayed on the screen.

Acceptance Criteria:
•	The application must refuse to start and immediately halt all internal processes.
•	The system must display a fatal error message exactly reading: "FATAL ERROR 004: Audit Trail Integrity Check Failed".
•	Details inside the error message must mention the security violation or tampered entry.

---
**Document Approval Signatures**
(To be signed upon finalization)
