# Appendix 4: Functional Testing

| Document Control Information | Details |
|------------------------------|---------|
| **Project/System Name**      | Air Quality Review System (AQR) |
| **System Identifier**        | AQR-SYS-01 |
| **Document Version**         | 1.1.0 |

---

SECTION 1: OBJECTIVE
This document is established to specify the functional specification and define the functional testing methodology for the Air Quality Review (AQR) System. The objective is to verify that the software system operates in accordance with the user requirements (URS), specifically focusing on validating the system's analytical outputs (e.g., 25-minute rules, pressure comparisons) against provided inputs.

SECTION 2: PROCEDURE
1.	Execute test scenarios using pre-defined Mock Data CSV files to simulate the system’s analytical functionality.
2.	Documentation: Record all functional outcomes in the Test Result section to confirm the integrity of the developed features.
3.	Reporting: Summarize the testing status and any functional deviations encountered.

SECTION 3: GENERAL DOCUMENTS
3.1 Attachment 1: Signature List
All personnel involved in the recording, reviewing, and verifying of testing documentation are required to provide their signatures in Attachment 1.
3.2 Attachment 2: Work Instruction Verification
Specify the details of the User Manuals associated with the testing process.
3.3 Protocol Correction
Any planned or unplanned deviations from the testing steps or Acceptance Criteria must be documented.
3.4 Attachment 5: User Comments and Enhancement Requests Record
Any recommendations from QA identified during testing shall be recorded.
3.5 Attachment 6: System Error Record
In the event of system calculation errors, findings must be documented.

SECTION 4: RESPONSIBILITY
| Actions | Responsibilities |
|---------|------------------|
| Perform Testing | Validation Engineer |
| Review Results | CSV Specialist & GMP Specialist |
| Approve Results | QA Manager |

SECTION 5: TEST CASE SELECTION PROCEDURE
Test selection for Functional Testing is based on the core business logic described in the User Requirements Specification (URS). Key functional areas include temperature/humidity limit evaluations, the strict 25-minute excursion continuity rule, the 10-minute gap reset threshold, and the differential pressure synchronization logic.

SECTION 6: TEST RESULT
1.	OQ-TC-01: Business Date Adjustment (Minus 1 Day Logic)
Objective: 
To verify that the system correctly subtracts one day from the date found in the raw data filename. Many sensors save data for "Yesterday" at 00:05 AM "Today." To make sure the report shows the correct day the air was actually measured, the system must automatically move the date back by one day.
Procedure:
1.	Select the test file named `1-P050_04-06-26_00-00.csv`.
2.	Process this file using the AQR application.
3.	Open the resulting Excel report in the `./reports/` folder.
4.	Locate the cell labeled "Date of Review".
Acceptance Criteria:
The cell "Date of Review" correctly displays the value " 05 Apr 2026".
Result: [   ] P   [   ] CP   [   ] F   [   ] N/A


2.	OQ-TC-04: Temperature High Limit (Sustained 25-Min Excursion)
Objective:
To verify that 6 consecutive points (25 mins) above the limit trigger a failure.
Procedure:
1.	Open the AQR application.
2.	In `SetPointLimit.xlsx`, set the High Limit to 25.0°C.
3.	Select the CSV file where 6 consecutive data points at 5-minute intervals, the temperature value more than 25°C.
4.	Process the file ('Analyze' button) and check the result status.
5.	Select the CSV file with up to 5 consecutive data points at 5-minute intervals where temperature value over 25°C.
6.	Process the file ('Analyze' button) and check the result status.
Acceptance Criteria:
Result status in the report shows: `Out of Spec` (✗) and `Passed` (✓) respectively.
Result: [   ] P   [   ] CP   [   ] F   [   ] N/A


3.	OQ-TC-05: Temperature Continuity Rule (Data Gap Handling)
Objective:
To verify that missing data points prevent a violation from being reported.
Procedure:
1.	Open the AQR application.
2.	In `SetPointLimit.xlsx`, set the High Limit to 25.0°C.
3.	Select the data file where 3 points of temperature value more than 25°C, followed by a 10-minute gap (one point within 25°C), then 3 or more points over 25.0°C.
4.	Process the file ('Analyze' button) and check the result status.
Acceptance Criteria:
Result status in the report shows: `Passed` (✓) caused by the system correctly identifies that there was no continuous 25-minute violation.
Result: [   ] P   [   ] CP   [   ] F   [   ] N/A


4.	OQ-TC-06: Humidity High Limit (Sustained 25-Min Excursion)
Objective:
Confirm that sustained high humidity (above 65%) is flagged correctly.
Procedure:
1.	Open the AQR application.
2.	In `SetPointLimit.xlsx`, set the Humidity High Limit to 65.0%RH.
3.	Select the CSV file where 6 consecutive data points at 5-minute intervals, the humidity value more than 65.0%RH.
4.	Process the file ('Analyze' button) and check the result status.
5.	Select the CSV file with up to 5 consecutive data points at 5-minute intervals, where the humidity values over 65.0%RH.
6.	Process the file ('Analyze' button) and check the result status.
Acceptance Criteria:
Result status in the report shows: `Out of Spec` (✗) and `Passed` (✓) respectively.
Result: [   ] P   [   ] CP   [   ] F   [   ] N/A


5.	OQ-TC-07: Humidity Low Limit (Sustained 25-Min Excursion)
Objective:
Confirm that sustained low humidity (below 35%) is flagged correctly.
Procedure:
1.	Open the AQR application.
2.	In `SetPointLimit.xlsx`, set the Humidity Low Limit to 35.0%RH.
3.	Select the CSV file where 6 consecutive data points at 5-minute intervals, the humidity value below 35%RH.
4.	Process the file ('Analyze' button) and check the result status.
5.	Select the CSV file with up to 5 consecutive data points at 5-minute intervals, where the humidity values under 35%RH.
6.	Process the file ('Analyze' button) and check the result status.
Acceptance Criteria:
Result status in the report shows: `Out of Spec` (✗) and `Passed` (✓) respectively.
Result: [   ] P   [   ] CP   [   ] F   [   ] N/A


6.	OQ-TC-08: Humidity Continuity Rule (Data Gap Handling)
Objective:
To verify that missing data points prevent a violation from being reported.
Procedure:
1.	Open the AQR application.
2.	In `SetPointLimit.xlsx`, set the Humidity Low Limit to 65.0%RH.
3.	Select the data file with 3 points of humidity value over 65%RH, followed by a 10-minute gap (one point equal to or less than 64.9%RH), then 3 points over 65.0%RH.
4.	Process the file ('Analyze' button) and check the result status.
Acceptance Criteria:
Result status in the report shows: `Passed` (✓) caused by the system correctly identifies that there was no continuous 25-minute violation.
Result: [   ] P   [   ] CP   [   ] F   [   ] N/A


7.	OQ-TC-09: Humidity Separating Low/High Limit Rule
Objective:
To verify that the system can detect the separate low/high out of the limit and reporting in the separating format.
Procedure:
1.	Open the AQR application.
2.	In `SetPointLimit.xlsx`, set the Humidity Low Limit to 35.0%RH and Humidity High Limit to 65%RH.
3.	Select the data file where at least 6 consecutive points, the humidity value are over 65.0%RH, followed by 6 or more consecutive points which the humidity value below 35%RH.
4.	Process the file ('Analyze' button) and check the result status.
Acceptance Criteria:
Result status in the report shows: `Out of Spec` (✗) followed by detailed separating interval that relative humidity out of low limit and high limit.
Result: [   ] P   [   ] CP   [   ] F   [   ] N/A


8.	OQ-TC-10: Pressure Corridor Check: 'within' status (For Room Pressure Setpoint 15 and 30 Pa)
Objective: 
Verify that the system flags a room when its pressure is lower than the corridor pressure.
Procedure:
1.	Open the AQR application.
2.	In `SetPointLimit.xlsx`, set the Pressure Low Limit, Pressure High Limit, and Room Pressure Comparison as per expected room pressure condition.
3.	Select data where room pressure value is over or under the room Pressure High or Low Limit for 6 consecutive respectively, but less than corridor pressure value at the same timestamp.
4.	Process the file ('Analyze' button) and check the result status.
Acceptance Criteria:
Result status in the report shows: `Passed` (✓) and status string shows: `within` Corridor.
Result: [   ] P   [   ] CP   [   ] F   [   ] N/A


9.	OQ-TC-11: Pressure Corridor Check: 'over' status (For Room Pressure Setpoint 15 and 30 Pa)
Objective:
Verify that if a room is over its own internal limit and above the corridor, it is flagged as 'over'.
Procedure:
1.	Open the AQR application.
2.	In `SetPointLimit.xlsx`, set the Pressure Low Limit, Pressure High Limit, and Room Pressure Comparison as per expected room pressure condition.
3.	Select data where room pressure value is over or under the room Pressure High or Low Limit for 6 consecutive respectively, and over corridor pressure value at the same timestamp.
4.	Process the file ('Analyze' button) and check the result status.
Acceptance Criteria:
Result status in the report shows: `Out of Spec` (✗) and status string shows: `over` Corridor.
Result: [   ] P   [   ] CP   [   ] F   [   ] N/A


10.	OQ-TC-12: Pressure Corridor Check: 'within' status (For Room Pressure Setpoint 45 Pa)
Objective: 
Verify that the system flags a room when its pressure is higher than the corridor pressure.
Procedure:
1.	Open the AQR application.
2.	In `SetPointLimit.xlsx`, set the Pressure Low Limit, Pressure High Limit, and Room Pressure Comparison as per expected room pressure condition.
3.	Select data where room pressure value is over or under the room Pressure High or Low Limit for 6 consecutive respectively, but more than corridor pressure value at the same timestamp.
4.	Process the file ('Analyze' button) and check the result status.
Acceptance Criteria:
Result status in the report shows: `Passed` (✓) and status string shows: `over` Corridor.
Result: [   ] P   [   ] CP   [   ] F   [   ] N/A


11.	OQ-TC-13: Pressure Corridor Check: 'under' status (For Room Pressure Setpoint 45 Pa)
Objective:
Verify that if a room is over its own internal limit and below the corridor, it is flagged as 'under'.
Procedure:
1.	Open the AQR application.
2.	In `SetPointLimit.xlsx`, set the Pressure Low Limit, Pressure High Limit, and Room Pressure Comparison as per expected room pressure condition.
3.	Select data where room pressure value is over or under the room Pressure High or Low Limit for 6 consecutive respectively, and under corridor pressure value at the same timestamp.
4.	Process the file ('Analyze' button) and check the result status.
Acceptance Criteria:
Result status in the report shows: `Out of Spec` (✗) and status string shows: `under` Corridor.
Result: [   ] P   [   ] CP   [   ] F   [   ] N/A


12.	OQ-TC-14: UI Transformation: Main Plant, Module 5, and Pilot Splitter Logic
Objective:
To verify that the system can split a bulk Main Plant (RMT, RMH, and RPT), Module 5, Pilot scale files into individual room CSVs.
Procedure:
1.	Open the AQR application.
2.	Navigate to Data Transformation module in the left sidebar.
3.	Upload a bulk CSV file containing data for different rooms.
4.	Click the 'Split Report' button in the AQR application.
5.	Navigate to the generated output folder.
Acceptance Criteria:
•	A new folder has been created with a timestamped name.
•	The folder contains individual CSV files, one for each room for number equal to bulk CSV file.
Result: [   ] P   [   ] CP   [   ] F   [   ] N/A


13.	OQ-TC-15: UI Filter: Date Range Selection Accuracy
Objective:
To ensure the report only contains data points within the selected date range.
Procedure:
1.	Open the AQR application.
2.	Select the `SetPointLimit.xlsx` and CSV files for 01 Mar 2026 to 10 Mar 2026.
3.	Set the UI date filter to start on 01-Mar and end on 05-Mar.
4.	Process a dataset containing data for the entire month of March.
Acceptance Criteria:
The final Excel report only displays rows with timestamps from March 1st to March 5th.
Result: [   ] P   [   ] CP   [   ] F   [   ] N/A


14.	OQ-TC-16: UI Filter: Room/Location Exclusion Logic
Objective:
Verify the system can ignore specific rooms if they are not selected in the checklist.
Procedure:
1.	Open the AQR application.
2.	Select the `SetPointLimit.xlsx` and CSV files for at least Module 1 and other room CSV files.
3.	In the AQR UI Room List, uncheck the box for "Module 1".
4.	Run the analysis for the whole building.
Acceptance Criteria:
The final Excel report does not contain any data or sheets for Module 1.
Result: [   ] P   [   ] CP   [   ] F   [   ] N/A


15.	OQ-TC-17: Robustness: Corrupt Data Value Handling (Non-numeric data)
Objective:
Verify that the system skips "garbage" data (like "Data Loss" or "No Data") without crashing.
Procedure:
1.	Open the AQR application.
2.	Select the `SetPointLimit.xlsx` and CSV files for at non-numeric data CSV files.
3.	Process the file ('Analyze' button) and check the result status.
Acceptance Criteria:
•	The system completes the analysis without errors.
•	Result status in the report shows: `Data Loss` and period of its.
•	A "Warning" entry regarding the non-numeric data is recorded in `audit_trail.log`.
Result: [   ] P   [   ] CP   [   ] F   [   ] N/A


16.	OQ-TC-18: System Versioning and Report Metadata Traceability
Objective: 
To ensure the final report proves which version of the software was used.
Procedure:
1.	Generate any standard report and open the Excel file.
2.	Look for the "Software Version" and "Generation Date" fields.
Acceptance Criteria:
The software version (e.g., v1.1.0) is clearly printed on the report.
Result: [   ] P   [   ] CP   [   ] F   [   ] N/A


17.	OQ-TC-20: Logical Limit Constraint Validation
Objective:
To prevent the entry of logically impossible limits (e.g., High Limit < Low Limit).
Procedure:
1.	Open `SetPointLimit.xlsx` and set Humidity High Limit to 35%RH and Low Limit to 65%RH.
2.	Save and attempt to run an analysis.
Acceptance Criteria:
The system displays: "ERR-006: Configuration Error - High Limit cannot be lower than Low Limit."
Result: [   ] P   [   ] CP   [   ] F   [   ] N/A


18.	OQ-TC-21: System Clock & Timestamp Synchronization
Objective:
To verify that audit logs match the local workstation system clock.
Procedure:
1.	Note the current Windows System Time.
2.	Perform an action in the AQR application.
3.	Check the timestamp of that action in `audit_trail.log`.
Acceptance Criteria:
The log timestamp matches the Windows clock.
Result: [   ] P   [   ] CP   [   ] F   [   ] N/A


19.	OQ-TC-22: User Identity Capture (OS-Level Traceability)
Objective:
To verify that the system identifies the Windows User account performing the actions.
Procedure:
1.	Open `audit_trail.log` and inspect the "User" field of the last entry.
Acceptance Criteria:
The "User" field exactly matches the currently logged-in Windows Username.
Result: [   ] P   [   ] CP   [   ] F   [   ] N/A


20.	OQ-TC-25: Audit Trail Missing File Handling
Objective:
To ensure the system refuses to run if the audit trail file is deleted. If the history of the system's actions is missing, the system cannot be considered "validated" or "secure." Deleting the log file is a common way to hide unauthorized actions, so the system must prevent this.
Procedure:
1.	Ensure the AQR application is completely closed.
2.	Open Windows File Explorer and navigate to the `./logs/` directory.
3.	Select the `audit_trail.log` file and press the `Delete` key.
4.	Attempt to launch `AirQualityReview.exe`.
Acceptance Criteria:
•	The application fails to launch the main processing interface.
•	The system automatically creates a new, empty `audit_trail.log` file.
Result: [   ] P   [   ] CP   [   ] F   [   ] N/A


SECTION 7: CRITERIA FOR EVALUATION OF TEST RESULT
| Types of Test Result | Description |
|----------------------|-------------|
| Pass (P) | The test results align with the predefined expectations and requirements. |
| Conditionally Pass (CP) | The test results were inconsistent. Discrepancies have been documented for further corrective action. |
| Fail (F) | Test results fail to meet predefined criteria. Retesting is required after system correction. |
| Not Available (N/A) | Not applicable for this specific test case. |

SECTION 8: REFERENCE
•	User Requirement Specification (URS)
•	Functional Specification (FS)
•	Operational Qualification (OQ) Protocol

SECTION 9: TERMS AND DEFINITION
•	**Functional Testing:** Testing the software against the functional requirements/specifications.
•	**Excursion:** A period where environmental data falls outside the acceptable limits.

SECTION 10: ATTACHMENT
•	Attachment 1: Signature List
•	Attachment 7: Test Result Sheet
