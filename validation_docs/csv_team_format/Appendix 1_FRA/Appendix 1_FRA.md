# Appendix 1: Functional Risk Assessment (FRA)

| Document Control Information | Details |
|------------------------------|---------|
| **Project/System Name**      | Air Quality Review System (AQR) |
| **System Identifier**        | AQR-SYS-01 |
| **Document Version**         | 1.1.0 |

---

SECTION 1: OBJECTIVE
This document outlines the Functional Risk Assessment (FRA) for the Air Quality Review (AQR) System. The objective is to proactively identify potential software failures, evaluate their impact on product quality and data integrity (GxP impact), and define necessary technical controls and testing requirements to mitigate these risks.

SECTION 2: PROCEDURE
The risk assessment is conducted using the Failure Mode and Effects Analysis (FMEA) methodology.
•	Identify potential failure modes for each User Requirement.
•	Assess Severity (S), Probability of occurrence (P), and Detectability (D).
•	Calculate the Risk Priority Number (RPN) = S × P × D.
•	Establish technical mitigations and trace them to specific testing protocols (OQ/PQ).

SECTION 3: GENERAL DOCUMENTS
3.1 Attachment 1: Signature List
All personnel involved in the recording, reviewing, and verifying of this risk assessment are required to provide their signatures in Attachment 1.
3.2 Attachment 4: Deviation Log & Report
Any deviations found during the risk assessment process must be documented in Attachment 4.

SECTION 4: RESPONSIBILITY
| Actions | Responsibilities |
|---------|------------------|
| Perform Risk Assessment | Coding Specialist & CSV Specialist |
| Review Assessment | GMP Specialist & Documentation Specialist |
| Approve Assessment | Project Manager / System Owner |

SECTION 5: TEST CASE SELECTION PROCEDURE & RISK CRITERIA
Risks are evaluated using the Failure Mode and Effects Analysis (FMEA) methodology on a 1-5 scale.
• **Severity (S)**: 1=Negligible, 2=Minor, 3=Moderate, 4=Critical, 5=Catastrophic.
• **Probability (P)**: 1=Rare, 2=Unlikely, 3=Possible, 4=Likely, 5=Almost certain.
• **Detectability (D)**: 1=Excellent, 2=Good, 3=Moderate, 4=Poor, 5=Undetectable.

**Risk Priority Class (RPN = S x P x D)**:
• **LOW**: 1-26 (Acceptable)
• **MEDIUM**: 27-63 (Unacceptable - needs mitigation). *Note: Any S=3 is at least Medium.*
• **HIGH**: 64-125 (Intolerable - needs elimination). *Note: Any S=4 or 5 is High.*

SECTION 6: TEST RESULT

| No. | ID | Risk Scenario | Impact | S | Cause | Control | P | D | RPN | Class | Mitigation Control | Test Ref | S_R | P_R | D_R | RPN_R | Class_R |
|:---:|:---:|:---|:---|:---:|:---|:---|:---:|:---:|:---:|:---|:---|:---|:---:|:---:|:---:|:---:|:---|
| 1 | FRA-01 | **Calculation Error:**<br>System might miscalculate excursion duration.<br>(e.g., counting 20 mins as 25). | Data integrity loss:<br>False violation reporting. | 3 | Logic error in timestamp subtraction. | Manual audit of rows. | 1 | 4 | 12 | MED* | Enforce strict 6-point logic for 25-minute threshold rules. | FT: OQ-TC-04, 06, 07;<br>RT: PQ-TC-02 | 3 | 1 | 1 | 3 | LOW |
| 2 | FRA-02 | **Continuity Error:**<br>System might "connect the dots" across data gaps,<br>creating fake violation periods. | Inaccurate violation periods on report. | 3 | Large time gaps in raw source CSV data. | Manual audit of source vs report. | 1 | 4 | 12 | MED* | Verify 5-minute intervals; reset calculation if gap > 10 minutes. | FT: OQ-TC-05, 08;<br>RT: PQ-TC-02 | 3 | 1 | 1 | 3 | LOW |
| 3 | FRA-03 | **Desync:**<br>Accidental comparison of Room A data (10:00 AM)<br>with Corridor data (10:05 AM). | False pressure hierarchy violations. | 4 | High complexity in data joining logic. | None currently. | 2 | 4 | 32 | HIGH** | Use strict "Inner Join" on exact timestamps for all rooms. | FT: OQ-TC-10, 11, 12, 13 | 4 | 1 | 1 | 4 | LOW |
| 4 | FRA-04 | **Tamper Vulnerability:**<br>Manual editing of audit log in Notepad<br>to hide mistakes or change history. | Compliance failure:<br>Records are not secure. | 4 | Plain text log files are accessible. | None. | 2 | 4 | 32 | HIGH** | Implement SHA-256 Hash-chaining for every log entry. | MT: IQ-TC-06;<br>InT: OQ-TC-23;<br>RT: PQ-TC-03 | 4 | 1 | 1 | 4 | LOW |
| 5 | FRA-05 | **Deployment Failure:**<br>Application fails to open on new PC due to<br>missing icons or hardcoded paths. | System unavailability and delays. | 3 | Path resolution issues on new workstations. | Crash is highly visible. | 2 | 2 | 12 | MED* | Use "Path-Independent" logic for internal assets. | MT: IQ-TC-01, 04;<br>InT: IQ-TC-08;<br>RT: PQ-TC-03 | 3 | 1 | 1 | 3 | LOW |
| 6 | FRA-06 | **Data Skewing:**<br>Network glitch causing duplicate data rows,<br>leading to double-counting time. | Inaccurate statistics;<br>Double-counting duration. | 3 | Glitches in sensor/network transmission. | Requires row-by-row manual check. | 2 | 3 | 18 | MED* | Programmatically perform a "Deduplication" pass. | RT: PQ-TC-02 | 3 | 1 | 1 | 3 | LOW |
| 7 | FRA-07 | **Data Destruction:**<br>Software bug accidentally overwriting<br>original raw sensor data files. | Irrecoverable loss of original GxP records. | 4 | Logic error in file handling code. | Visible only after data is lost. | 1 | 3 | 12 | HIGH** | Enforce strict "Read-Only" commands at code level. | MT: IQ-TC-01;<br>InT: OQ-TC-24 | 4 | 1 | 1 | 4 | LOW |
| 8 | FRA-08 | **Mapping Error:**<br>System moves Room A temperature data<br>into Room B's file during splitting. | Incorrect data attribution to location. | 3 | Inconsistent room naming in bulk file. | Hard to detect if values are similar. | 2 | 3 | 18 | MED* | Use intelligent "Regex" pattern recognition. | FT: OQ-TC-14;<br>RT: PQ-TC-04 | 3 | 1 | 1 | 3 | LOW |
| 9 | FRA-09 | **Data Loss:**<br>System fails to capture all records from<br>very large bulk files (audit gaps). | Incomplete records; missing excursions. | 3 | Buffer overflows during processing. | Visible only if checking row counts. | 1 | 3 | 9 | MED* | Implement row count verification and footer checks. | FT: OQ-TC-14;<br>RT: PQ-TC-04 | 3 | 1 | 1 | 3 | LOW |
| 10 | FRA-10 | **Header Integrity:**<br>Split CSV has corrupted format that analysis<br>software cannot read. | Analysis engine fails to open the file. | 3 | Logic error in CSV structure reconstruction. | Highly visible error during analysis. | 1 | 3 | 9 | MED* | Standardize header logic using defined templates. | InT: OQ-TC-19;<br>FT: OQ-TC-14;<br>RT: PQ-TC-04 | 3 | 1 | 1 | 3 | LOW |

**Note:** S=Severity, P=Probability, D=Detectability, RPN=Risk Priority Number (_R indicates Residual Risk).
\*Minimum Medium due to S=3 rule. \**High Risk due to S=4/5 rule.

SECTION 8: REFERENCE
•	User Requirement Specification (URS)
•	Functional Specification (FS)
•	ISPE GAMP 5 (Second Edition)

SECTION 9: TERMS AND DEFINITION
•	**FMEA:** Failure Mode and Effects Analysis
•	**RPN:** Risk Priority Number
•	**GxP:** Good Practice quality guidelines and regulations

SECTION 10: ATTACHMENT
•	Attachment 1: Signature List
•	Attachment 4: Deviation List and Deviation Reports
