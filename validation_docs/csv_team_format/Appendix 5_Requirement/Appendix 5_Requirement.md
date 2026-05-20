# Appendix 5: Requirement Testing

| Document Control Information | Details |
|------------------------------|---------|
| **Project/System Name**      | Air Quality Review System (AQR) |
| **System Identifier**        | AQR-SYS-01 |
| **Document Version**         | 1.1.0 |

---

SECTION 1: OBJECTIVE
This document is established to specify the Requirement Testing methodology for the Air Quality Review (AQR) System. The objective is to monitor and evaluate the system's operational stability, throughput performance, and its ability to meet the high-level User Requirements (URS) under real-world, heavy workload conditions.

SECTION 2: PROCEDURE
1.	Execute test scenarios using massive, real-world datasets spanning an extended period.
2.	Documentation: Record all performance outcomes and system stability observations in the Test Result section.
3.	Reporting: Summarize the testing status and record any application crashes or prolonged processing delays.

SECTION 3: GENERAL DOCUMENTS
3.1 Attachment 1: Signature List
All personnel involved must provide their signatures in Attachment 1.
3.2 Attachment 2: Work Instruction Verification
Detail the Work Instructions (WI) associated with the testing process.
3.3 Protocol Correction
Deviations from the procedure or Acceptance Criteria must be documented.
3.4 Attachment 5: User Comments and Enhancement Requests Record
Any recommendations from Key Users/Super Users shall be recorded.
3.5 Attachment 6: System Error Record
In the event of system errors (e.g., Out of Memory), all findings must be documented.

SECTION 4: RESPONSIBILITY
| Actions | Responsibilities |
|---------|------------------|
| Perform Testing | Key User / Super User |
| Review Results | CSV Specialist & Validation Lead |
| Approve Results | Quality Assurance (QA) Director |

SECTION 5: TEST CASE SELECTION PROCEDURE
The test selection for Requirement Testing focuses on system boundaries, data volume handling, and long-term stability. The goal is to ensure the system is robust enough to handle a full month's worth of data for an entire facility without failure, fully satisfying the operational User Requirements.

SECTION 6: TEST RESULT

1.	PQ-TC-01: Monthly Data Load Throughput (Performance)
Objective:
To ensure the application handles production-level volumes (150+ files, >50MB) without failure or performance degradation.
Procedure:
•	System Launch: Launch `AirQualityReview.exe`.
•	Directory Selection: Select the folder containing 150 CSV files.
•	Baseline Monitoring: Record initial Memory usage in Task Manager.
•	Analysis Execution: Start a stopwatch and click 'Analyze'.
•	Continuous Monitoring: Note any "Not Responding" events or CPU spikes > 90% for more than 10 seconds.
•	Completion: Stop stopwatch upon completion and record final Memory usage.
Acceptance Criteria:
•	Analysis completes in under 5.0 minutes.
•	Memory usage increase (Post-analysis minus Baseline) is less than 200MB.
•	The system remains stable with no fatal hangs.
•	Evidence: Screenshots of Task Manager (Before/After) and Stopwatch.
Results: The program is highly resource-efficient; it processed 233 CSV files in under 10 seconds with minimal CPU and RAM usage based on testing computer specification as figure below.

2.	PQ-TC-02: End-to-End Result Reconciliation (GxP Accuracy)
Objective:
To verify decision-making accuracy by reconciling automated results against a manual analysis. This test ensures the 5-minute sampling and 10-minute gap logic is applied consistently (ALCOA+ Accuracy).
Procedure:
•	Manual Review: analyzes a "Complex Day" CSV manually, identifying all 25-minute violations and gap resets.
•	System Analysis: Process the same file through AQR.
•	Reconciliation: Match every timestamped interval in the report against the SME log.
Acceptance Criteria:
•	100% Correlation: All Start/End times, Min/Max values, and Status strings (Passed/Out of Spec) match perfectly.
Results: Proven Reliability: Over 1 year of real deployment demonstrated 100% correlation between manual reviews and the AQR system analysis. All critical data points including timestamps, Min/Max values, and Pass/Fail statuses match perfectly."

3.	PQ-TC-03: Business Continuity (Restore & Standalone Reliability)
Objective:
Verify application portability across local drives.
Procedure:
•	Move the root folder to drive `D:\`.
•	Launch `app.exe` and process a test file.
Acceptance Criteria:
•	Application launches and processes data without path-resolution errors.
•	Audit trail correctly records the new path in its metadata header.
Results: Complied with the acceptance criteria.

4.	PQ-TC-04: Production Data Transformation Lifecycle
Objective:
Verify end-to-end reliability of bulk-to-room CSV splitting.
Procedure:
•	Split a set of bulk production files using the Transformation module.
•	Verify 100% room extraction.
•	Perform a bit-for-bit comparison of 3 random room files against the source.
Acceptance Criteria:
•	No data loss or character corruption during splitting.
•	Transformed CSVs include the mandatory "End of Report" footer.
•	Evidence: Screenshot of the comparison between source bulk and extracted CSV data.
Results: Complied with the acceptance criteria.

5.	PQ-TC-06: System Stability during Extended GUI Session
Objective:
Verify no significant memory leaks over an 8-hour shift.
Procedure:
•	Keep AQR open for 8 hours, performing an analysis run every hour.
•	Record memory usage after each run.
Acceptance Criteria:
•	At the end of 8 hours, the "Idle Memory Usage" must be within 50MB of the initial "Idle Memory Usage" at Start.
•	All 8 analysis runs must complete successfully.
Results: Complied with the acceptance criteria.



SECTION 7: CRITERIA FOR EVALUATION OF TEST RESULT
| Types of Test Result | Description |
|----------------------|-------------|
| Pass (P) | The test results align with the predefined expectations and requirements of the Key Users. |
| Conditionally Pass (CP) | The test results were inconsistent with the key user’s expectations. Discrepancies documented. |
| Fail (F) | Test results fail to meet predefined criteria. Retesting is required. |
| Not Available (N/A) | Not applicable. |

SECTION 8: REFERENCE
•	User Requirement Specification (URS)
•	Performance Qualification (PQ) Protocol

SECTION 9: TERMS AND DEFINITION
•	**Requirement Testing:** Testing that validates the system meets all documented user and business needs.
•	**Throughput:** The amount of data processed by the system in a given amount of time.

SECTION 10: ATTACHMENT
•	Attachment 1: Signature List
•	Attachment 7: Test Result Sheet
