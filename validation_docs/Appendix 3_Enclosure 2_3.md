
**Enclosure 2: Test Script**



| Test ID | Test Scenario | Expected Result |
| --- | --- | --- |
| Error Handling Verification | Error Handling Verification | Error Handling Verification |
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
| System Transformation | System Transformation | System Transformation |
|  | The system transforms manually generated BAS/EMS files into the required raw data format. | The system transforms the data into the required raw data format and saves it in the designated folder. |
| InT-01 check_reverse_violations | InT-01 check_reverse_violations | InT-01 check_reverse_violations |
| InT-01-1 | The system correctly detects and reports data when a high-pressure room (≥35 Pa) drops below the corridor pressure, triggering a Corridor "Over" Room violation. | The system must print a structured table log capturing the OVER violation details.<br>The function must return a list containing the formatted time range and specific violation type. |
| InT-01-2 | The system correctly detects and reports data when a low-pressure room (< 35 Pa) spikes above the corridor pressure, triggering a Corridor "Under" Room violation. | The system must print a structured table log capturing the UNDER violation details.<br>The function must return a list containing the formatted time range and specific violation type. |
| InT-01-3 | The system successfully merges data with a timestamp difference ≤ 60 seconds, while ignoring rows exceeding the 60-second limit. | The function only output the violation line for the timestamp difference ≤ 60 seconds.<br>The unmatched timestamp must be evaluated as NaN and effectively removed. |
| InT-01-4 | The find_compare_path function properly extracts room identifiers from file paths and correctly matches them with the configured corridor rooms. | The function must return a tuple matching the designated configuration structure. |
| InT-02 _compute_plot_result | InT-02 _compute_plot_result | InT-02 _compute_plot_result |
| InT-02-1 | The system correctly extracts chart datasets and accurately identifies temperature/humidity violations that persist across at least 6 continuous rows (min_length=6). | The system presents exactly 1 temperature violation counter and 1 humidity violation counter. Pressure must be 0 because it has no spec limits configured. |
| InT-02-2 | Any metric violation lasting fewer than 6 consecutive rows is successfully filtered out and ignored by the interval logic loop. | All violation numbers must return 0 because the pressure deviation loop requires a minimum index duration trace length of 6 rows. |
| InT-02-3 | The missing data (NaN or None) within the data tables does not crash the script, is excluded from calculations and is properly replaced with None in datasets. | The system handles missing items securely without returning exceptions. |
| InT-03 Get_plot_info | InT-03 Get_plot_info | InT-03 Get_plot_info |
| InT-03-1 | The system correctly discovers and groups matching .csv files inside nested directories, correctly parses room IDs, filters out unselected rooms, and executes downstream chart computation tasks seamlessly. | Room data can be mapped when both the raw data from uploaded files and the contents of the limit file are present. |
| InT-03-2 | Verify that if an individual raw data file is corrupt and throws an unhandled exception during its parsing cycle (prepare_df), the script logs the event details to the system's audit_trail module without terminating the execution loop. | The system intercepts the prepare_df error exception and dispatches an event in audit trail log.<br>The execution flow moves safely onto subsequent loops instead of breaking, returning an empty query payload context. |
| InT-04 _analyze_single_room_core | InT-04 _analyze_single_room_core | InT-04 _analyze_single_room_core |
| InT-04-1 | The parameter violations are only logged into the final analysis, if they persist continuously for ≥ 25 minutes. Transient spikes below the 25-minute mark must be ignored. | Terminal Diagnostics prints only the target dataframe subset corresponding to index window <br>The text registers Fail strictly for the 25-minute interval block, while omitting the transient spike block entirely. |
| InT-04-2 | The missing sensor readings (NaN) are explicitly flagged as Data Loss and are safely concatenated onto existing limit violation indicators in the final output text block. | The text registers Fail and Data Loss at the time of the event. |
| InT-04-3 | The room pressure is out of limit settings but remains mathematically accept its associated corridor reference, it is downgraded to a false alarm. Conversely, if it drops below/above the corridor, it must trigger a fail indicator. |  |
| InT-05 analyze_files | InT-05 analyze_files | InT-05 analyze_files |
| InT-05-1 | The script scans files successfully, filters chronological intervals based on a pre-built data cache index, builds wide Excel pivot matrices with GAMP 5 tracking version metadata, and outputs full statistical execution summaries without runtime interference. | Audit Trail log include ANALYSIS_START, FILE_PROCESSED, FILE_ERROR, ROOM_SKIPPED_ERROR and ANALYSIS_SUCCESS.<br>Summary results contain full dataset profiles along with absolute data statistics tracking (plot_result metadata)<br>Excel Report includes Software Version v1.1.0. and column configurations expand to wide-format layout mapping. |
| InT-06 Analyze_files_phase2 | InT-06 Analyze_files_phase2 | InT-06 Analyze_files_phase2 |
| InT-06-1 | The function maps complex multi-file room paths (RMT/RMH/RDP), hashes initial parsed rows, runs temporal daily partitions, groups wide-table results, and logs GAMP 5 compliance parameters properly. | Audit Trail log include ANALYSIS_START, FILE_PROCESSED, FILE_ERROR, ROOM_SKIPPED_ERROR and ANALYSIS_SUCCESS.<br>Summary results contain full dataset profiles along with absolute data statistics tracking (plot_result metadata)<br>Excel Report includes Software Version v1.1.0. and column configurations expand to wide-format layout mapping. |

