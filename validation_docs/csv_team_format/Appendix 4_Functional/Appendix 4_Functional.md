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

SECTION 6: TEST RESULT

1.	OQ-TC-01: Business Date Adjustment (Minus 1 Day Logic)
Objective:
To verify that the system correctly the date found in the raw data. Many sensors save data for "Yesterday" at 00:05 AM "Today." To make sure the report shows the correct day the air was actually measured, the system must automatically find the correctly measured day.
Procedure:
•	Navigate to the application root directory.
•	Select the test file named `1-P033_04-07-26_00-00.csv`.
•	Process this file using the AQR application.
•	Open the resulting Excel report in the `./reports/` folder.
•	Locate the merged cell labeled "DATE: [ANALYZED DAY]".
Acceptance Criteria:
•	The cell "DATE: [ANALYZED DAY]" correctly displays the value "DATE: 2026-04-06".
Results:

2.	OQ-TC-04: Temperature High Limit (Sustained 25-Min Excursion)
Objective:
To verify that 6 consecutive (25 mins) temperature points above the limit trigger a failure.
Procedure:
•	Open the AQR application.
•	In `SetPointLimit.xlsx`, set the High Limit to 25.0°C.
•	Select the CSV file where 6 consecutive data points at 5-minute intervals, the temperature value more than 25°C.
•	Process the file ('Analyze' button) and check the result status.
•	Select the CSV file with up to 5 consecutive data points at 5-minute intervals where temperature value over 25°C.
•	Process the file ('Analyze' button) and check the result status.
Acceptance Criteria:
•	Result status in the report shows: `Out of Spec` (✗) and `Passed` (✓) respectively.
Results:

3.	OQ-TC-05: Temperature Continuity Rule (Data Gap Handling)
Objective:
To verify that missing data points prevent a violation from being reported.
Procedure:
•	Open the AQR application.
•	In `SetPointLimit.xlsx`, set the High Limit to 25.0°C.
•	Select the data file where 5 points of temperature value more than 25°C, followed by a 10-minute gap (one point within 25°C), then 5 points over 25.0°C.
•	Process the file ('Analyze' button) and check the result status.
Acceptance Criteria:
•	Result status in the report shows: `Passed` (✓) caused by the system correctly identifies that there was no continuous 25-minute violation.
Results:

4.	OQ-TC-06: Humidity High Limit (Sustained 25-Min Excursion)
Objective:
Confirm that sustained high humidity (above 65%) is flagged correctly.
Procedure:
•	Open the AQR application.
•	In `SetPointLimit.xlsx`, set the Humidity High Limit to 65.0%RH.
•	Select the first CSV file where 6 consecutive data points at 5-minute intervals, the humidity value more than 65.0%RH.
•	Process the file ('Analyze' button) and check the result status.
•	Select the second CSV file with up to 5 consecutive data points at 5-minute intervals, where the humidity values over 65.0%RH.
•	Process the file ('Analyze' button) and check the result status.
Acceptance Criteria:
•	Result status in the report shows: `Out of Spec` (✗) and `Passed` (✓) respectively.
Results:

5.	OQ-TC-07: Humidity Low Limit (Sustained 25-Min Excursion)
Objective:
Confirm that sustained low humidity (below 35%) is flagged correctly.
Procedure:
•	Open the AQR application.
•	In `SetPointLimit.xlsx`, set the Humidity Low Limit to 35.0%RH.
•	Select the first CSV file where 6 consecutive data points at 5-minute intervals, the humidity value below 35%RH.
•	Process the file ('Analyze' button) and check the result status.
•	Select the second CSV file with up to 5 consecutive data points at 5-minute intervals, where the humidity values under 35%RH.
•	Process the file ('Analyze' button) and check the result status.
Acceptance Criteria:
•	Result status in the report shows: `Out of Spec` (✗) and `Passed` (✓) respectively.
Results:

6.	OQ-TC-08: Humidity Continuity Rule (Data Gap Handling)
Objective:
To verify that missing data points prevent a violation from being reported.
Procedure:
•	Open the AQR application.
•	In `SetPointLimit.xlsx`, set the Humidity Low Limit to 65.0%RH.
•	Select the data file with 5 points of humidity value over 65%RH, followed by a 10-minute gap (one point equal to or less than 64.9%RH), then 5 points over 65.0%RH.
•	Process the file ('Analyze' button) and check the result status.
Acceptance Criteria:
•	Result status in the report shows: `Passed` (✓) caused by the system correctly identifies that there was no continuous 25-minute violation.
Results:

7.	OQ-TC-09: Humidity Separating Low/High Limit Rule
Objective:
To verify that the system can detect the separate low/high out of the limit and reporting in the separating format.
Procedure:
•	Open the AQR application.
•	In `SetPointLimit.xlsx`, set the Humidity Low Limit to 35.0%RH and Humidity High Limit to 65%RH.
•	Select the data file where at least 6 consecutive points, the humidity value are over 65.0%RH, followed by 6 or more consecutive points which the humidity value below 35%RH.
•	Process the file ('Analyze' button) and check the result status.
Acceptance Criteria:
•	Result status in the report shows: `Out of Spec` (✗) followed by detailed separating interval that relative humidity out of low limit and high limit.
Results:

8.	OQ-TC-10: Pressure Corridor Check: 'within' status (For Room Pressure Setpoint 15 and 30 Pa)
Objective:
Verify that the system flags a room when its pressure is lower than the corridor pressure.
Procedure:
•	Open the AQR application.
•	In `SetPointLimit.xlsx`, set the Pressure Low Limit, Pressure High Limit, and Room Pressure Comparison as per expected room pressure condition.
•	Select data where room pressure value is over or under the room Pressure High or Low Limit for 6 consecutive respectively, but less than corridor pressure value at the same timestamp.
•	Process the file ('Analyze' button) and check the result status.
Acceptance Criteria:
•	Result status in the report shows: `Passed` (✓) and status string shows: `within` Corridor.
Results:

9.	OQ-TC-11: Pressure Corridor Check: 'over' status (For Room Pressure Setpoint 15 and 30 Pa)
Objective:
Verify that if a room is over its own internal limit and above the corridor, it is flagged as 'over'.
Procedure:
•	Open the AQR application.
•	In `SetPointLimit.xlsx`, set the Pressure Low Limit, Pressure High Limit, and Room Pressure Comparison as per expected room pressure condition.
•	Select data where room pressure value is over or under the room Pressure High or Low Limit for 6 consecutive respectively, and one point of them is over corridor pressure value at the same timestamp.
•	Process the file ('Analyze' button) and check the result status.
Acceptance Criteria:
•	Result status in the report shows: `Out of Spec` (✗) and status string shows: `over` Corridor.
Results:

10.	OQ-TC-12: Pressure Corridor Check: 'within' status (For Room Pressure Setpoint 45 Pa)
Objective:
Verify that the system flags a room when its pressure is higher than the corridor pressure.
Procedure:
•	Open the AQR application.
•	In `SetPointLimit.xlsx`, set the Pressure Low Limit, Pressure High Limit, and Room Pressure Comparison as per expected room pressure condition.
•	Select data where room pressure value is over or under the room Pressure High or Low Limit for 6 consecutive respectively, but more than corridor pressure value at the same timestamp.
•	Process the file ('Analyze' button) and check the result status.
Acceptance Criteria:
•	Result status in the report shows: `Passed` (✓) and status string shows: `over` Corridor.
Results:

11.	OQ-TC-13: Pressure Corridor Check: 'under' status (For Room Pressure Setpoint 45 Pa)
Objective:
Verify that if a room is over its own internal limit and below the corridor, it is flagged as 'under'.
Procedure:
•	Open the AQR application.
•	In `SetPointLimit.xlsx`, set the Pressure Low Limit, Pressure High Limit, and Room Pressure Comparison as per expected room pressure condition.
•	Select data where room pressure value is over or under the room Pressure High or Low Limit for 6 consecutive respectively, and one point of them is under corridor pressure value at the same timestamp.
•	Process the file ('Analyze' button) and check the result status.
Acceptance Criteria:
•	Result status in the report shows: `Out of Spec` (✗) and status string shows: `under` Corridor.
Results:

12.	OQ-TC-14: UI Transformation: Main Plant, Module 5, and Pilot Splitter Logic
Objective:
To verify that the system can split a bulk Main Plant (RMT, RMH, and RPT), Module 5, Pilot scale files into individual room CSVs.
Procedure:
•	Open the AQR application.
•	Navigate to Data Transformation module in the left sidebar.
•	Upload a bulk CSV file containing data for different rooms.
•	Click the 'Split Report' button in the AQR application.
•	Navigate to the generated output folder.
Acceptance Criteria:
•	A new folder has been created with a timestamped name.
•	The folder contains individual CSV files, one for each room for number equal to bulk CSV file.
Results: All files have been created in the correct format.

13.	OQ-TC-15: UI Filter: Date Range Selection Accuracy
Objective:
To ensure the report only contains data points within the selected date range.
Procedure:
•	Open the AQR application.
•	Select the `SetPointLimit.xlsx` and CSV files for 01 Apr 2026 to 10 Apr 2026.
•	Set the UI date filter to start on 06 Apr 2026 00:00 and end on 06 Apr 2026 23:55.
•	Process a dataset containing data for the entire month of March.
Acceptance Criteria:
•	The final Excel report only displays rows with timestamps from 06 Apr 2026.
Results: Complied with the acceptance criteria.

14.	OQ-TC-16: UI Filter: Room/Location Exclusion Logic
Objective:
Verify the system can ignore specific rooms if they are not selected in the checklist.
Procedure:
•	Open the AQR application.
•	Select the `SetPointLimit.xlsx` and CSV files for at least Module 1 and other room CSV files.
•	In the AQR UI Room List, uncheck the box for "Module 1".
•	Run the analysis for the whole building.
Acceptance Criteria:
•	The final Excel report does not contain any data or sheets for Module 1.
Results:

15.	OQ-TC-17: Robustness: Corrupt Data Value Handling (Non-numeric data)
Objective:
Verify that the system skips "garbage" data (like "Data Loss" or "No Data") without crashing.
Procedure:
•	Open the AQR application.
•	Select the `SetPointLimit.xlsx` and CSV files for at non-numeric data CSV files.
•	Process the file ('Analyze' button) and check the result status.
Acceptance Criteria:
•	The system completes the analysis without errors.
•	Result status in the report shows: `Data Loss` and period of its.
•	A "Warning" entry regarding the non-numeric data is recorded in `audit_trail.log`.
Results:

16.	OQ-TC-18: System Versioning and Report Metadata Traceability
Objective:
To ensure the final report proves which version of the software was used.
Procedure:
•	Generate any standard report and open the Excel file.
•	Look for the "Software Version: v1.1.0" and "Generated Date" fields.
Acceptance Criteria:
•	The software version is clearly printed on the report.
Results:

17.	OQ-TC-20: Logical Limit Constraint Validation
Objective:
To prevent the entry of logically impossible limits (e.g., High Limit < Low Limit).
Procedure:
•	Open `SetPointLimit.xlsx` and set Humidity High Limit to 35%RH and Low Limit to 65%RH or set Humidity Low Limit to 70%RH and High Limit to 65%RH.
•	Save and attempt to run an analysis.
Acceptance Criteria:
•	The system displays: "ERR-006: Configuration Error - High Limit cannot be lower than Low Limit or Low Limit cannot be higher than High Limit."
Results:

18.	OQ-TC-21: System Clock & Timestamp Synchronization
Objective:
To verify that audit logs match the local workstation system clock.
Procedure:
•	Note the current Windows System Time.
•	Perform an action in the AQR application.
•	Check the timestamp of that action in `audit_trail.log`.
Acceptance Criteria:
•	The log timestamp matches the Windows clock.
Results:

19.	OQ-TC-22: User Identity Capture (OS-Level Traceability)
Objective:
To verify that the system identifies the Windows User account performing the actions.
Procedure:
•	Open `audit_trail.log` and inspect the "User" field of the last entry.
Acceptance Criteria:
•	The "User" field exactly matches the currently logged-in Windows Username.
Results:




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
