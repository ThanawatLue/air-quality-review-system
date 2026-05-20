import pandas as pd
import os

def excel_to_md_appendix1(excel_path, md_path):
    # Read the risk sheet
    df = pd.read_excel(excel_path, sheet_name='FMEA', header=None)
    
    # Standard FMEA columns are usually:
    # No, Requirement, Failure Mode, Cause, Impact, S, P, D, RPN, Class, Mitigation, Trace
    # Let's find the header row (e.g. contains "No.")
    header_idx = 0
    for i, row in df.iterrows():
        if "No." in [str(x).strip() for x in row.values]:
            header_idx = i
            break
    
    df.columns = df.iloc[header_idx]
    df = df.iloc[header_idx+1:]
    
    # Remove rows where "No." column is NaN
    df = df[df.iloc[:, 0].notna()]
    
    # Filter to relevant columns if they exist
    # For Appendix 1, we usually want the core FMEA table.
    table_md = df.to_markdown(index=False)
    
    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()
        
    start_marker = "SECTION 6: TEST RESULT"
    end_marker = "SECTION 8: REFERENCE"
    
    start_idx = md_content.find(start_marker)
    end_idx = md_content.find(end_marker)
    
    if start_idx != -1 and end_idx != -1:
        final_md = md_content[:start_idx + len(start_marker)] + "\n\n" + table_md + "\n\n" + md_content[end_idx:]
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(final_md)
            print("Appendix 1 updated from Excel.")

root = r"d:\ex_work\AirQualityReview_Project\validation_docs\csv_team_format\Appendix 1_FRA"
excel_path = os.path.join(root, "Risk_Assessment_FMEA.xlsx")
md_path = os.path.join(root, "Appendix 1_FRA.md")
excel_to_md_appendix1(excel_path, md_path)
