# Consolidated Validation Test Scripts & Enclosures
### Air Quality Review (AQR) System — GAMP 5 Category 5 Validation Protocol

---

> [!NOTE]
> **Operational Verification**: This document combines the Unit / Module Test Scripts (Appendix 2) and the Integration / Error Handling Test Scripts (Appendix 3) into a single, cohesive test execution framework for GxP validation.


## Part 1: Module & Unit Verification (Appendix 2)
This section verifies individual functional software sub-modules and mathematical calculation invariants in the backend pandas engine.


### 1. Software Installation Verification


| Module ID | Test Scenario / สคริปต์การทดสอบ | Expected Result / ผลลัพธ์ที่คาดหวัง |
| :--- | :--- | :--- |
| MT-01 | PyInstaller correctly packages the software source code into a standalone, compact executable file. | PyInstaller must successfully compile the target script with zero critical warnings or errors in the build log.<br>The compact executable file can be deployed and executed on other computers without requiring a pre-installed Python environment. |
| MT-01 | The system's automated environment initialization capabilities, ensuring that necessary report folders and the security log file are correctly created during the initial runtime. | The `./reports` folder is automatically generated and present.<br>The `./logs` folder is automatically generated and present.<br>The `audit_trail.log` file is successfully initialized and located securely within the `./logs` directory. |
| MT-01 | The delivered program (`AirQualityReview.exe`) is correctly installed, matches the officially validated software build, and contains the correct version information. | Product Version explicitly displays "v1.1.0".<br>The generated SHA-256 hash perfectly matches the Master Build Record |
| MT-01 | The software's ability to "self-heal". If critical folders are accidentally deleted, the system must be able to automatically recreate them to prevent crashing. | The application launches successfully without displaying any system errors.<br>The system automatically re-creates the missing `./logs` and `./reports` folders to restore functionality. |


### 1. Logic Integrity Verification


| Module ID | Test Scenario / สคริปต์การทดสอบ | Expected Result / ผลลัพธ์ที่คาดหวัง |
| :--- | :--- | :--- |
| MT-02<br>(get_file_hash) | The calculate hash for a valid existing file, modification file and invalid file can be strictly detected. | Valid existing file - The function returns a valid 64-character SHA-256 hexadecimal string.<br>Modification file – The function returns a different 64-character SHA-256 hexadecimal string compared to the original file.<br>Invalid file - The function returns an error. |
| MT-03<br>(find_header) | <>Date keyword that located at the beginning of the file (Index 0), after multiple rows, and missing from the file are detected correctly. | The function successfully detects and returns the correct row index. |
| MT-04 <br>(find_point_<br>mapping) | The room ID and point type mapping function successfully achieves an exact match and handles all validation criteria, including: full room IDs with specific point types, auto-detection mode when point type is omitted, room ID format variations, multiple partial matches scoring, non-existent target room IDs, and empty input lists. | The function successfully achieves a match by pairing the precise Room ID with its specified point type. <br>The function successfully handles all validation criteria, including non-existent target room IDs, omitted point types, and empty input lists. |
| MT-05 (find_continuous<br>_ranges) | The function accurately detects continuous index sequences, establishes precise boundaries (Start, End) for each problem identified range, and handles distinct data gaps | The function accurately identifies both single and multiple continuous sequences, returning the complete range from start to end.<br>The function successfully handles empty lists and non-sequential data by returning an empty list []. |
| MT-06 <br>(get_file_date<br>_range) | The function correctly extracts the first and last valid date entries from a CSV file and gracefully handles structural anomalies or empty datasets. | The function accurately identifies standard data, formatting noise, and single-row dates, returning the correct start and end dates.<br>The function successfully handles outlier dates of 2001–2099, file empty, lacks any valid date and invalid file path. |
| MT-07<br>(prepare_df) | The function correctly loads raw CSV logs into a standardized DataFrame, automatically handles missing optional columns and file-naming extractions, and purges duplicate timestamp entries. | the function returns a standardized, cleaned DataFrame containing the reindexed columns: DateTime, Temperature, Humidity, and Pressure. All sensor data rows must be verified as successfully cast to numeric data types with no syntax exceptions. |
| MT-08<br>(find_compare<br>_path) | The system reliably maps cleanroom pressure data to its designated comparison room based on master setpoint profiles. | The system successfully maps the target cleanroom's pressure data to its designated comparison room profile and returns the correct file path. |
| MT-09<br>(parse_filename<br>_for_datetime) | The function consistently enforces the minus-1-day legacy business rule across all valid inputs. | the function accurately extracts date and time components from standard filenames, successfully executes error coercion, and correctly subtracts exactly one day from the parsed timestamp. |
| MT-10<br>(prepare_df<br>_phase2) | The function correctly loads Temperature (RMT), Humidity (RMH), and Pressure (RDP) files for the specific room into a standardized DataFrame. | The function successfully verifies the presence of Temperature (RMT), Humidity (RMH), and Pressure (RDP) files for the specific room, subsequently cleaning the datasets, aligning their timestamps, and merging them into a single, unified DataFrame. |
| MT-11<br>(get_file_date<br>_range_phase2) | The function correctly extracts the start and end date entries from a multiple raw data CSV file and gracefully handles structural anomalies or empty datasets. | The function successfully aggregates data across multiple raw CSV files to extract the absolute start and end dates.<br>The function successfully accommodates structural anomalies and entirely corrupted datasets by discarding invalid entries, ensuring continuous execution and returning (None, None) if no valid timestamps remain. |


## Part 2: Integration, System Transformation & Error Verification (Appendix 3)
This section verifies system integration limits, cross-room pressure correlations, raw file transformations, and security audit log error handlers.


### 2. Error Handling Verification


| Test ID | Test Scenario / สคริปต์การทดสอบ | Expected Result / ผลลัพธ์ที่คาดหวัง |
| :--- | :--- | :--- |
| ERR-001 | [Raw data] non-compliant raw data format (Header not found) | The system indexes headers from raw data files in the required format. If any other format is detected, the system will reject it and trigger warning code ERR-001. |
| ERR-002 | [Limit] missing limit specification | The system detects missing limit file and trigger warning code ERR-002. |
| ERR-003 | [Raw data & Limit] invalid data types. | The module detects and blocks non-numeric values by trigger warning code ERR-003. |
| ERR-004 | [Audit log] subsequent tampering with the audit trail log | The system detects any subsequent tampering with the audit trail log and triggers warning code ERR-004. |
| ERR-005 | [Raw data & Limit] A parameter limit is defined but its corresponding raw data is missing. | The module detects scenarios where a parameter limit is defined but its corresponding raw data is missing with trigger warning code ERR-005. |
| ERR-006 | [Limit] Inverted cross-limit inputs (High < Low). | The system detects mathematical logic integrity and rejects inverted cross-limit inputs (High < Low) with trigger warning code ERR-006. |
| ERR-007 | [Report] fail of data analysis and report generation. | The system detects failure of report generation with trigger warning code ERR-007. |
| ERR-008 | [Raw data] identical duplicate data at the same timestamp. | The system detects any identical duplicate data, output warning code ERR-008, and automatically record to the audit trail log containing the filename, room ID, and timestamps. |
| ERR-009 | [Limit] Non-Compliant limit format | The system indexes headers from raw data files in the required format. If any other format is detected, the system trigger warning code ERR-009. |
| ERR-010 | Cross-uploading raw data between Phase I and Phase II screens. | The system detects invalid raw data file and triggers warning code ERR-010 |
| ERR-000 | [Raw data] The module detects missing or null in raw data files | The system identifies missing or null data in raw data files and includes a corresponding remark in the summary report. |


### 2. System Transformation


| Test ID | Test Scenario / สคริปต์การทดสอบ | Expected Result / ผลลัพธ์ที่คาดหวัง |
| :--- | :--- | :--- |
|  | The system transforms manually generated BAS/EMS files into the required raw data format. | The system transforms the data into the required raw data format and saves it in the designated folder. |


### 2. InT-01 check_reverse_violations


| Test ID | Test Scenario / สคริปต์การทดสอบ | Expected Result / ผลลัพธ์ที่คาดหวัง |
| :--- | :--- | :--- |
| InT-01-1 | The system correctly detects and reports data when a high-pressure room (≥35 Pa) drops below the corridor pressure, triggering a Corridor "Over" Room violation. | The system must print a structured table log capturing the OVER violation details.<br>The function must return a list containing the formatted time range and specific violation type. |
| InT-01-2 | The system correctly detects and reports data when a low-pressure room (< 35 Pa) spikes above the corridor pressure, triggering a Corridor "Under" Room violation. | The system must print a structured table log capturing the UNDER violation details.<br>The function must return a list containing the formatted time range and specific violation type. |
| InT-01-3 | The system successfully merges data with a timestamp difference ≤ 60 seconds, while ignoring rows exceeding the 60-second limit. | The function only output the violation line for the timestamp difference ≤ 60 seconds.<br>The unmatched timestamp must be evaluated as NaN and effectively removed. |
| InT-01-4 | The find_compare_path function properly extracts room identifiers from file paths and correctly matches them with the configured corridor rooms. | The function must return a tuple matching the designated configuration structure. |


### 2. InT-02 _compute_plot_result


| Test ID | Test Scenario / สคริปต์การทดสอบ | Expected Result / ผลลัพธ์ที่คาดหวัง |
| :--- | :--- | :--- |
| InT-02-1 | The system correctly extracts chart datasets and accurately identifies temperature/humidity violations that persist across at least 6 continuous rows (min_length=6). | The system presents exactly 1 temperature violation counter and 1 humidity violation counter. Pressure must be 0 because it has no spec limits configured. |
| InT-02-2 | Any metric violation lasting fewer than 6 consecutive rows is successfully filtered out and ignored by the interval logic loop. | All violation numbers must return 0 because the pressure deviation loop requires a minimum index duration trace length of 6 rows. |
| InT-02-3 | The missing data (NaN or None) within the data tables does not crash the script, is excluded from calculations and is properly replaced with None in datasets. | The system handles missing items securely without returning exceptions. |


### 2. InT-03 Get_plot_info


| Test ID | Test Scenario / สคริปต์การทดสอบ | Expected Result / ผลลัพธ์ที่คาดหวัง |
| :--- | :--- | :--- |
| InT-03-1 | The system correctly discovers and groups matching .csv files inside nested directories, correctly parses room IDs, filters out unselected rooms, and executes downstream chart computation tasks seamlessly. | Room data can be mapped when both the raw data from uploaded files and the contents of the limit file are present. |
| InT-03-2 | Verify that if an individual raw data file is corrupt and throws an unhandled exception during its parsing cycle (prepare_df), the script logs the event details to the system's audit_trail module without terminating the execution loop. | The system intercepts the prepare_df error exception and dispatches an event in audit trail log.<br>The execution flow moves safely onto subsequent loops instead of breaking, returning an empty query payload context. |


### 2. InT-04 _analyze_single_room_core


| Test ID | Test Scenario / สคริปต์การทดสอบ | Expected Result / ผลลัพธ์ที่คาดหวัง |
| :--- | :--- | :--- |
| InT-04-1 | The parameter violations are only logged into the final analysis, if they persist continuously for ≥ 25 minutes. Transient spikes below the 25-minute mark must be ignored. | Terminal Diagnostics prints only the target dataframe subset corresponding to index window <br>The text registers Fail strictly for the 25-minute interval block, while omitting the transient spike block entirely. |
| InT-04-2 | The missing sensor readings (NaN) are explicitly flagged as Data Loss and are safely concatenated onto existing limit violation indicators in the final output text block. | The text registers Fail and Data Loss at the time of the event. |
| InT-04-3 | The room pressure is out of limit settings but remains mathematically accept its associated corridor reference, it is downgraded to a false alarm. Conversely, if it drops below/above the corridor, it must trigger a fail indicator. |  |


### 2. InT-05 analyze_files


| Test ID | Test Scenario / สคริปต์การทดสอบ | Expected Result / ผลลัพธ์ที่คาดหวัง |
| :--- | :--- | :--- |
| InT-05-1 | The script scans files successfully, filters chronological intervals based on a pre-built data cache index, builds wide Excel pivot matrices with GAMP 5 tracking version metadata, and outputs full statistical execution summaries without runtime interference. | Audit Trail log include ANALYSIS_START, FILE_PROCESSED, FILE_ERROR, ROOM_SKIPPED_ERROR and ANALYSIS_SUCCESS.<br>Summary results contain full dataset profiles along with absolute data statistics tracking (plot_result metadata)<br>Excel Report includes Software Version v1.1.0. and column configurations expand to wide-format layout mapping. |


### 2. InT-06 Analyze_files_phase2


| Test ID | Test Scenario / สคริปต์การทดสอบ | Expected Result / ผลลัพธ์ที่คาดหวัง |
| :--- | :--- | :--- |
| InT-06-1 | The function maps complex multi-file room paths (RMT/RMH/RDP), hashes initial parsed rows, runs temporal daily partitions, groups wide-table results, and logs GAMP 5 compliance parameters properly. | Audit Trail log include ANALYSIS_START, FILE_PROCESSED, FILE_ERROR, ROOM_SKIPPED_ERROR and ANALYSIS_SUCCESS.<br>Summary results contain full dataset profiles along with absolute data statistics tracking (plot_result metadata)<br>Excel Report includes Software Version v1.1.0. and column configurations expand to wide-format layout mapping. |

