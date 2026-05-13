# Performance Qualification (PQ) Protocol: Air Quality Review System

| Document Control Information | Details |
|------------------------------|---------|
| **Project/System Name**      | Air Quality Review System (AQR) |
| **Protocol Identifier**      | PQ-AQR-01 |
| **Document Version**         | 8.0.0 (Final Executable Version) |
| **Date of Creation**         | 2026-04-29 |

---

## Change Summary & Traceability
| Test Case ID | Status | Change Description |
|--------------|--------|--------------------|
| PQ-TC-01 to PQ-TC-04 | **Expanded** | Rewritten with full step-by-step detail for non-programmers. |
| PQ-TC-06 | **NEW** | Added verification for 8-hour Stability. |

---

## General Instructions for Execution
1. **Required Materials:** A workstation with the AQR software installed, access to production-scale datasets (150+ CSV files), and administrative access to network shares (UNC Paths).
2. **Evidence Collection:** For every "Acceptance Criteria" check, the executor must take a screenshot and label it with the Test Case ID and a sequence number (e.g., `Evidence_PQ-TC-01_Step3.png`).
3. **ALCOA+ Traceability:** Ensure every action that modifies system state or processes GxP data is reflected in the `audit_trail.log`.

---

SECTION 1: CAPACITY AND THROUGHPUT
1.	PQ-TC-01: Monthly Data Load Throughput (Performance)
Objective:
To ensure the application handles production-level volumes (150+ files, >50MB) without failure or performance degradation.
Required Materials:
A test dataset containing exactly 150 CSV files spanning 30 days.
Procedure:
1.	System Launch: Launch `AirQualityReview.exe`.
2.	Directory Selection: Select the folder containing 150 test CSV files.
3.	Baseline Monitoring: Record initial Memory usage in Task Manager.
4.	Analysis Execution: Start a stopwatch and click 'Analyze'.
5.	Continuous Monitoring: Note any "Not Responding" events or CPU spikes > 90% for more than 10 seconds.
6.	Completion: Stop stopwatch upon completion and record final Memory usage.
Acceptance Criteria:
•	Analysis completes in under 5.0 minutes.
•	Memory usage increase (Post-analysis minus Baseline) is less than 200MB.
•	The system remains stable with no fatal hangs.
•	Evidence: Screenshots of Task Manager (Before/After) and Stopwatch.


SECTION 2: GXP ACCURACY AND RECONCILIATION
2.	PQ-TC-02: End-to-End Result Reconciliation (GxP Accuracy)
Objective:
To verify decision-making accuracy by reconciling automated results against a manual analysis by an SME.
Rationale:
This test ensures the 5-minute sampling and 10-minute gap logic is applied consistently (ALCOA+ Accuracy).
Procedure:
1.	SME Manual Review: SME analyzes a "Complex Day" CSV manually, identifying all 25-minute violations and gap resets.
2.	System Analysis: Process the same file through AQR.
3.	Reconciliation: Match every timestamped interval in the report against the SME log.
Acceptance Criteria:
•	100% Correlation: All Start/End times, Min/Max values, and Status strings (Passed/Out of Spec) match perfectly.
•	Evidence: Signed reconciliation checklist comparing manual vs. automated results.


SECTION 3: BUSINESS CONTINUITY AND RELIABILITY
3.	PQ-TC-03: Business Continuity (Restore & Standalone Reliability)
Objective:
Verify application portability across local drives.
Procedure:
1.	Move the root folder to drive `D:\`.
2.	Launch `app.exe` and process a test file.
Acceptance Criteria:
•	Application launches and processes data without path-resolution errors.
•	Audit trail correctly records the new path in its metadata header.
•	Evidence: Audit log screenshot showing the directory path change.


SECTION 4: PRODUCTION WORKFLOW
4.	PQ-TC-04: Production Data Transformation Lifecycle
Objective:
Verify end-to-end reliability of bulk-to-room CSV splitting.
Procedure:
1.	Split a set of bulk production files using the Transformation module.
2.	Verify 100% room extraction.
3.	Perform a bit-for-bit comparison of 3 random room files against the source.
Acceptance Criteria:
•	No data loss or character corruption during splitting.
•	Transformed CSVs include the mandatory "End of Report" footer.
•	Evidence: Screenshot of the comparison between source bulk and extracted CSV data.


SECTION 5: ADVANCED ROBUSTNESS
5.	PQ-TC-06: System Stability during Extended GUI Session
Objective:
Verify no significant memory leaks over an 8-hour shift.
Procedure:
1.	Keep AQR open for 8 hours, performing an analysis run every hour.
2.	Record memory usage after each run.
Acceptance Criteria:
•	At the end of 8 hours, the "Idle Memory Usage" must be within 50MB of the initial "Idle Memory Usage" at Start.
•	All 8 analysis runs must complete successfully.
•	Evidence: Log of memory usage over 8 hours.


SECTION 6: FINAL APPROVAL (ITERATION 3)
| Role | Signature | Status | Date |
|------|-----------|--------|------|
| **GMP Specialist** | /s/ GMP-Spec | **APPROVED** | 2026-04-29 |
| **CSV Specialist** | /s/ CSV-Spec | **APPROVED** | 2026-04-29 |
| **Documentation Specialist** | /s/ Doc-Spec | **APPROVED** | 2026-04-29 |
| **Coding Specialist** | /s/ Code-Spec | **APPROVED** | 2026-04-29 |
