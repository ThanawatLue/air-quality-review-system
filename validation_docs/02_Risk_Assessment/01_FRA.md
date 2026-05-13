# Functional Risk Assessment (FRA) - Team Format (Rev02)

| Document Control Information | Details |
|------------------------------|---------|
| **Project/System Name**      | Air Quality Review System (AQR) |
| **Document Ref**             | QP-AND3-001_Rev02 |
| **Document Version**         | 1.3.0 |

---

## SECTION 1: OBJECTIVE
This document defines the Functional Risk Assessment (FRA) for the Air Quality Review (AQR) System according to the Rev02 standards. The objective is to evaluate functional risks on a 1-5 scale and implement mitigations based on the revised RPN thresholds.

## SECTION 2: SCORING CRITERIA (Rev02)
- **Severity (S)**: 1=Negligible, 2=Minor, 3=Moderate, 4=Critical, 5=Catastrophic.
- **Probability (P)**: 1=Rare (<5%), 2=Unlikely (5-24%), 3=Possible (25-59%), 4=Likely (60-89%), 5=Almost certain (>90%).
- **Detectability (D)**: 1=Excellent (100% detect), 2=Good (Very likely), 3=Moderate, 4=Poor (Little chance), 5=Undetectable (No control).

**Risk Priority Class (RPN = S x P x D)**:
- **LOW**: 1 to 26 (Acceptable)
- **MEDIUM**: 27 to 63 (Unacceptable - needs mitigation). *Note: Any S=3 is at least Medium.*
- **HIGH**: 64 to 125 (Intolerable - needs elimination). *Note: Any S=4 or 5 is High.*

---

## SECTION 3: RISK ASSESSMENT TABLE (REVISED)

| No. | Module ID | Risk Scenario (Detailed Description) | Impact | S | Cause | Control | P | D | RPN | Class | Mitigation Control | Test Ref (MT/InT/FT/RT) | S | P | D | RPN | Class |
|:---:|:---:|:---|:---|:---:|:---|:---|:---:|:---:|:---:|:---:|:---|:---|:---:|:---:|:---:|:---:|:---:|
| 1 | FRA-01 | **Calculation Error**: The system might miscalculate the duration of a temperature excursion. For instance, if a room stays above the limit for 24 minutes but the system counts it as 25, it flags a false violation. | Data integrity loss: Incorrect excursion reporting leads to unnecessary investigations. | 3 | Logic error in the mathematical subtraction between timestamps. | Manual check or manual audit of rows. | 1 | 4 | 12 | Med* | Enforce strict 6-point logic for 25-minute threshold rules. | FT: OQ-TC-04, 06, 07; RT: PQ-TC-02 | 3 | 1 | 1 | 3 | Med |
| 2 | FRA-02 | **Continuity Error**: When data points are missing due to sensor downtime, the system might "connect the dots" across the gap, creating a fake violation period that didn't happen in reality. | Inaccurate violation periods shown on the report. | 3 | Large time gaps exist in the raw source CSV sensor data. | Manual audit of source files vs report. | 1 | 4 | 12 | Med* | Verify 5-minute intervals between every record; reset calculation if gap > 10 minutes. | FT: OQ-TC-05, 08; RT: PQ-TC-02 | 3 | 1 | 1 | 3 | Med |
| 3 | FRA-03 | **Desync**: When comparing pressure between two rooms, the system might accidentally compare Room A data from 10:00 AM with Corridor data from 10:05 AM, giving a wrong result. | False pressure hierarchy violations reported to the user. | 4 | High complexity in the data joining logic between multiple files. | None currently. | 2 | 4 | 32 | High** | Use strict "Inner Join" on exact timestamps for all rooms to ensure the pressure difference is always calculated using data from the same moment. | FT: OQ-TC-10, 11, 12, 13 | 4 | 1 | 1 | 4 | High |
| 4 | FRA-04 | **Tamper Vulnerability**: A user could manually open the audit log in Notepad and edit the text to hide a mistake or change the history of actions, breaking regulatory compliance (21 CFR Part 11). | Compliance failure: Electronic records are not secure or trustworthy. | 5 | Plain text log files are technically accessible on the Windows drive. | None. | 2 | 4 | 40 | High** | Implement SHA-256 Hash-chaining for every log entry. If any letter is changed manually, the "chain" breaks and the system alerts the team. | MT: IQ-TC-07; InT: OQ-TC-23; FT: OQ-TC-25; RT: PQ-TC-03 | 5 | 1 | 1 | 5 | High |
| 5 | FRA-05 | **Deployment Failure**: The application might fail to open on a new computer because it cannot find its internal icons, graphics, or hidden files due to hardcoded paths. | System unavailability and delay in quality review processes. | 3 | Path resolution issues when software is moved to different Windows workstations. | Application crash is highly visible. | 2 | 2 | 12 | Med* | Use "Path-Independent" logic to automatically search internal system folders for assets regardless of workstation. | MT: IQ-TC-01, 04; InT: IQ-TC-06; RT: PQ-TC-03 | 3 | 1 | 1 | 3 | Med |
| 6 | FRA-06 | **Data Skewing**: A sensor or network glitch might cause the same data row to be saved twice with the same timestamp, causing the system to double-count the time. | Inaccurate statistics; double-counting excursion duration. | 3 | Glitches in sensor or network transmission causing duplicate records. | Requires row-by-row manual check to identify. | 2 | 3 | 18 | Med* | Programmatically perform a "Deduplication" pass, automatically deleting any rows with duplicate timestamps before analysis. | RT: PQ-TC-02 | 3 | 1 | 1 | 3 | Med |
| 7 | FRA-07 | **Data Destruction**: A software bug could accidentally try to "Save" over the original raw sensor data files, corrupting or deleting the records required for audits. | Irrecoverable loss of original GxP data records required for audits. | 5 | Logic error in the file handling/saving part of the software code. | Visible only after the file is already lost. | 1 | 3 | 15 | High** | Enforce strict "Read-Only" commands at the code level so the software cannot physically modify source files. | MT: IQ-TC-05 | 5 | 1 | 1 | 5 | High |
| 8 | FRA-08 | **Mapping Error**: During file splitting, the system might get confused and accidentally move Room A's temperature data into Room B's file. | Incorrect data attribution: Data linked to wrong physical location. | 3 | Inconsistent room naming or formatting in the bulk source file. | Hard to detect if data values look similar. | 2 | 3 | 18 | Med* | Use intelligent "Regex" pattern recognition to securely lock data columns to their corresponding Room IDs. | FT: OQ-TC-14; RT: PQ-TC-04 | 3 | 1 | 1 | 3 | Med |
| 9 | FRA-09 | **Data Loss**: During processing of very large bulk files, the system might fail to capture all records, losing data from the end of the day. | Incomplete records leading to missing excursions or audit gaps. | 3 | Buffer overflows or premature "End of File" signals during processing. | Only visible if manually checking row counts. | 1 | 3 | 9 | Med* | Implement row count verification and specifically verify the presence of the mandatory "End of Report" footer text. | FT: OQ-TC-14; RT: PQ-TC-04 | 3 | 1 | 1 | 3 | Med |
| 10 | FRA-10 | **Header Integrity**: The newly split CSV file might have a corrupted or messy format that the analysis software cannot read, halting the review process. | Analysis engine fails to open the file, stopping the review process. | 3 | Logic error in the reconstruction of the CSV file structure. | Highly visible error during analysis step. | 1 | 3 | 9 | Med* | Standardize header reconstruction logic using a meticulously defined template to match original reports. | InT: OQ-TC-19; FT: OQ-TC-14; RT: PQ-TC-04 | 3 | 1 | 1 | 3 | Med |

---
*\*Minimum Medium due to S=3 rule.  \*\*High Risk due to S=4/5 rule.*

**END OF DOCUMENT**
