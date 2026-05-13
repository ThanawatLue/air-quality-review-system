# Master Validation Plan (MVP): Air Quality Review System

| Document Control Information | Details |
|------------------------------|---------|
| **Project/System Name**      | Air Quality Review System (AQR) |
| **System Identifier**        | AQR-SYS-01 |
| **GAMP 5 Category**          | Category 5 (Custom Built Application) |
| **Regulatory Context**       | GMP, 21 CFR Part 11, EU GMP Annex 11, PIC/S PI 011-3 |
| **Document Version**         | 13.0 (No OS ACL Edition - Approved by 4-Agent Committee) |
| **Date of Creation**         | 2026-04-22 |

---

SECTION 1: INTRODUCTION
The Air Quality Review (AQR) System is a custom-developed Python application designed to automate the compliance review of environmental monitoring data (such as Temperature, Humidity, and Differential Pressure). The system evaluates raw data files (in CSV format) exported from the Building Automation System (BAS). It compares this data against predefined acceptable limits, which are stored in an external Excel file (`SetPointLimit.xlsx`), to identify any violations or "excursions" that might affect product quality (GxP excursions).

The system enforces two main business rules:
•	25-Minute Continuous Violation Rule: A violation is only recorded if the out-of-spec condition lasts for a continuous 25 minutes.
•	Pressure Corridor Comparison: It compares the air pressure of cleanrooms against adjacent corridors to ensure proper airflow direction.

[Surgical Update]: The system logic is specifically designed for data that is recorded exactly every 5 minutes. It incorporates a "10-minute gap threshold", meaning that if the system misses a single 5-minute data record, it can still safely continue the analysis without breaking the continuity check.

This Master Validation Plan (MVP) defines the strategy and testing required to prove that the AQR system is reliable, accurate, "fit for intended use," and fully complies with regulatory standards such as 21 CFR Part 11 (rules for electronic records and signatures).

SECTION 2: SYSTEM DESCRIPTION AND BOUNDARIES

2.1 System Architecture & Delivery
The system is built using modern programming tools (Python for the core logic, Pandas for data processing, and Flask for the user interface). 

To make it easy for users, the system is packaged and delivered as a "Standalone Executable" (`app.exe`). This means the entire application is bundled into a single file that can run on any Windows computer immediately. Users do not need to install Python or any other programming tools. This approach also prevents accidental changes to the software's internal code, ensuring a secure and controlled environment.

2.2 System Boundaries
•	Inbound Boundary: The system's starting point is reading the raw CSV data files (recorded every 5 minutes) that are exported from the BAS system. (Note: Validating the BAS system itself is out-of-scope for this project).
•	System Boundary: This covers the execution of the `app.exe` file, which includes all the hidden calculation logic, the user interface on the screen, and the data splitting features.
•	Outbound Boundary: The system's endpoint is generating the final Excel summary report and securely saving a tamper-proof history log (`audit_trail.log`).

SECTION 3: SCOPE OF VALIDATION

3.1 In-Scope Components
The following components are within the scope of this validation plan:
•	Application Logic: All data processing, removing duplicate data rows, mapping data columns to specific rooms, and calculating the 25-minute violation rule.
•	Data Gap Continuity: The system's ability to calculate time gaps correctly, allowing a maximum of 10 minutes between records before it resets the violation counter.
•	Data Integrity & Security: The system's security features, including the tamper-evident "Hash-chained" Audit Trails (a secure logging method similar to blockchain), the digital fingerprinting (SHA-256 hashing) of source CSV files, and tracking changes to the Limit File (`SetPointLimit.xlsx`).
•	Deployment Integrity: Proving that the `app.exe` file can be reliably generated and that it correctly finds its internal files when running on a user's computer.

3.2 Out-of-Scope Components
•	Validation of the physical environmental sensors located in the facility.
•	Validation of the underlying Windows 10/11 Operating System.

SECTION 4: REGULATORY STRATEGY (21 CFR PART 11)
The AQR System is classified as a "Hybrid System" because it generates electronic records but might still rely on manual signatures for final approval.

•	11.10(c) Record Protection: The system strictly reads source CSV files in "Read-Only" mode to prevent accidental data modification. The audit logs use "hash chaining", an advanced cryptographic method that mathematically links each log entry to the previous one, making it impossible to secretly delete or alter history.
•	11.10(d) System Access: Access to run the software is restricted to authorized users who are logged into the Windows workstation.
•	11.10(e) Audit Trail: A secure, automatic log captures who used the system (User), what they did (Action), the digital fingerprints of the files used (File Hashes), and any modifications to the acceptable limits. A mandatory Standard Operating Procedure (SOP) will require Quality Assurance to periodically review this log.

SECTION 5: VALIDATION METHODOLOGY (GAMP 5)
The validation process strictly follows the internationally recognized ISPE GAMP 5 Second Edition V-Model methodology.

•	4-Agent Validation Committee: All documents and test results are iteratively reviewed and approved by four distinct roles: a GMP Specialist (Quality), a CSV Specialist (Validation), a Documentation Specialist, and a Coding Specialist.
•	Risk Assessment: A Functional Risk Assessment (FRA) is conducted using the Failure Mode and Effects Analysis (FMEA) method to identify and mitigate potential software failures before testing begins.

SECTION 6: DELIVERABLES AND ACCEPTANCE CRITERIA
•	Phases: The project is divided into six phases: Phase 1 (Planning: VP, URS), Phase 2 (Risk & Function: FRA, FS), Phase 3 (Design: DS, CS), Phase 4 (Installation: IQ, CRR), Phase 5 (Operation: OQ), and Phase 6 (Performance: PQ, RTM, VSR).
•	Acceptance Criteria: 100% of the User Requirements must be traced and proven by approved Operational (OQ) and Performance (PQ) test cases. There must be zero open critical or major deviations at the end of the project.

---
**Document Approval Signatures**
(To be signed upon finalization)
