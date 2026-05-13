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

SECTION 6: TEST RESULT (RISK ASSESSMENT TABLE)
| Risk ID | URS Reference | Potential Failure Mode | S | P | D | RPN | Risk Class | Mitigation Strategy / Technical Control | OQ/PQ Test Reference |
|:---:|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---|:---|
| FRA-01 | UR-FN-03 | **Calculation Error**: The system might miscalculate the duration of a temperature excursion. For instance, if a room stays above the limit for 24 minutes but the system counts it as 25, it flags a false violation. | 3 | 1 | 4 | 12 | Medium* | Enforce strict 6-point logic for 25-min threshold. | OQ-TC-04, 06, 07, PQ-TC-02 |
| FRA-02 | UR-FN-04 | **Continuity Error**: When data points are missing due to sensor downtime, the system might "connect the dots" across the gap, creating a fake violation period that didn't happen. | 3 | 1 | 4 | 12 | Medium* | Verify 5-min intervals; reset count if gap > 10 min. | OQ-TC-05, 08, PQ-TC-02 |
| FRA-03 | UR-FN-05 | **Desync**: When comparing pressure between two rooms, the system might accidentally compare Room A data from 10:00 AM with Corridor data from 10:05 AM, giving a wrong result. | 4 | 2 | 4 | 32 | High** | Use Inner Join on exact timestamps for all rooms to ensure the pressure difference is always calculated using data from the same moment. | OQ-TC-10, 11, 12, 13 |
| FRA-04 | UR-DI-01 | **Tamper Vulnerability**: A user could manually open the audit log in Notepad and edit the text to hide a mistake or change the history of actions, breaking regulatory compliance. | 5 | 2 | 4 | 40 | High** | Implement SHA-256 Hash-chaining for every log entry. If any letter is changed manually, the "chain" breaks and the system alerts the team. | IQ-TC-07 (App 2), OQ-TC-23 (App 3), OQ-TC-25 (App 4) |
| FRA-05 | UR-OP-01 | **Deployment Failure**: The application might fail to open on a new computer because it cannot find its internal icons, graphics, or hidden files due to hardcoded paths. | 3 | 2 | 2 | 12 | Medium* | Use dynamic path searching logic to locate all internal assets regardless of the workstation. | IQ-TC-01 (App 2), IQ-TC-04 (App 2), IQ-TC-06 (App 3) |
| FRA-06 | UR-FN-07 | **Data Skewing**: A sensor or network glitch might cause the same data row to be saved twice with the same timestamp, causing the system to double-count the time. | 3 | 2 | 3 | 18 | Medium* | Programmatically drop duplicate timestamp rows before starting analysis. | PQ-TC-02 |
| FRA-07 | UR-DI-05 | **Data Destruction**: A software bug could accidentally try to "Save" over the original raw sensor data files, corrupting or deleting the records required for audits. | 5 | 1 | 3 | 15 | High** | Enforce strict Read-Only commands at the code level so the software cannot physically modify source files. | IQ-TC-05 |
| FRA-08 | UR-FN-09 | **Mapping Error**: During file splitting, the system might get confused and accidentally move Room A's temperature data into Room B's file. | 3 | 2 | 3 | 18 | Medium* | Use intelligent Regex pattern recognition to securely lock data columns to their corresponding Room IDs. | OQ-TC-14, PQ-TC-04 |
| FRA-09 | UR-FN-09 | **Data Loss**: During processing of very large bulk files, the system might fail to capture all records, losing data from the end of the day. | 3 | 1 | 3 | 9 | Medium* | Implement row count verification and check for the mandatory "End of Report" footer. | OQ-TC-14, PQ-TC-04 |
| FRA-10 | UR-FN-09 | **Header Integrity**: The newly split CSV file might have a corrupted or messy format that the analysis software cannot read, halting the review process. | 3 | 1 | 3 | 9 | Medium* | Standardize header reconstruction logic to match the exact, validated structure of the original sensor reports. | OQ-TC-14 (App 4), OQ-TC-19 (App 3) |

*\*Minimum Medium due to S=3 rule.*  *\*\*High Risk due to S=4/5 rule.*

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
