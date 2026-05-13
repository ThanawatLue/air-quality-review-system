# Requirements Traceability Matrix (RTM): Air Quality Review System

| Document Control Information | Details |
|------------------------------|---------|
| **Project/System Name**      | Air Quality Review System (AQR) |
| **Document Version**         | 13.0 (Full Content - IOP Aligned Edition) |

---

SECTION 1: REQUIREMENTS TRACEABILITY MATRIX

| URS ID | Requirement Description | FS Ref | IQ Verif | OQ Verif | PQ Verif |
|--------|-------------------------|--------|----------|----------|----------|
| UR-OP-01 | Standalone Executable (`app.exe`) | 1.1 | IQ-TC-01 | - | PQ-TC-03 |
| UR-OP-02 | Local Web GUI (Port 5000) | 1.1 | IQ-TC-04 | OQ-TC-14, 15 | PQ-TC-01, PQ-TC-06 |
| UR-OP-03 | Server-Side Folder Browser | 2.1 | - | OQ-TC-14, 24 | - |
| UR-OP-04 | Date Picker Selection | 2.1 | - | OQ-TC-15 | - |
| UR-OP-05 | External Limit File (Excel) | 2.1 | IQ-TC-02 | OQ-TC-02, 03, 20 | - |
| UR-OP-06 | Excel Report Output | 2.2 | IQ-TC-05 | OQ-TC-01, 15, 18 | - |
| UR-FN-01 | Header Parsing (`<>Date`) | 2.2 | - | OQ-TC-19 | - |
| UR-FN-02 | Point Mapping Logic | 2.2 | - | OQ-TC-14 | - |
| UR-FN-03 | 25-Minute Rule (Strict Continuity) | 2.2 | - | OQ-TC-04, 06, 07 | PQ-TC-02 |
| UR-FN-04 | 10-Minute Gap Reset Rule | 2.2 | - | OQ-TC-05, 08 | PQ-TC-02 |
| UR-FN-05 | Pressure Corridor Delta | 2.2 | - | OQ-TC-10, 11, 12, 13 | - |
| UR-FN-06 | Min, Max, Mean Stats | 2.2 | - | OQ-TC-09 | - |
| UR-FN-07 | Deduplication Logic | 2.2 | - | - | PQ-TC-02 |
| UR-FN-08 | Software Versioning (v1.1.0) | 2.2 | - | OQ-TC-18 | - |
| UR-FN-09 | Data Transformation Module | 2.3 | - | OQ-TC-14 | PQ-TC-04 |
| UR-DI-01 | Secure Audit Trail (Hash-chain) | 2.3 | IQ-TC-03 | OQ-TC-23, 25 | PQ-TC-03 |
| UR-DI-02 | Audit Trail Content (User/TS) | 2.3 | - | OQ-TC-21, 22 | - |
| UR-DI-03 | Source File SHA-256 Hashing | 2.3 | - | OQ-TC-24 | PQ-TC-03 |
| UR-DI-04 | Limit File SHA-256 Hashing | 2.3 | - | OQ-TC-02, 03 | - |
| UR-DI-05 | Read-Only Source Access | 2.3 | IQ-TC-05 | - | - |
| UR-DI-06 | Error Exception Modals | 2.3 | - | OQ-TC-02, 03, 19, 20, 23 | - |
| UR-DI-07 | Backup Compatibility | 2.3 | IQ-TC-07 | - | - |
| UR-DI-08 | Binary Integrity (SHA-256) | 2.3 | IQ-TC-01 | - | - |
| UR-RP-01 | Report Columns (Room, Spec) | 2.2 | - | OQ-TC-14 | - |
| UR-RP-02 | Date Grouping Rows | 2.2 | - | OQ-TC-15 | - |
| UR-RP-03 | "Passed" Status Text | 2.2 | - | OQ-TC-04, 06, 07, 10, 12 | - |
| UR-RP-04 | Start/End Time List | 2.2 | - | OQ-TC-09 | - |
| UR-RP-05 | Times New Roman, Size 11 | 2.2 | - | OQ-TC-18 | - |

SECTION 2: VERIFICATION SUMMARY
*Note to CSV Team: In accordance with the factory's documentation structure, IQ Test Cases are mapped into Appendix 2 (Module) & Appendix 3 (Integration). OQ Test Cases are mapped into Appendix 3 & Appendix 4 (Functional). PQ Test Cases are mapped into Appendix 3 & Appendix 5 (Requirement).*

27 out of 27 User Requirements (100%) have been successfully traced and verified against the expanded Installation Qualification (IQ), Operational Qualification (OQ), and Performance Qualification (PQ) test suites. This provides documented evidence that the system fulfills all design and business requirements.
