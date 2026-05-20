import os
import subprocess
import re

def get_git_file(file_path):
    git_path = file_path.replace("\\", "/")
    if "AirQualityReview_Project/" in git_path:
        git_path = git_path.split("AirQualityReview_Project/")[1]
    
    result = subprocess.run(["git", "show", f"HEAD:{git_path}"], capture_output=True, text=True, encoding="utf-8")
    if result.returncode == 0:
        return result.stdout
    return ""

def extract_test_cases(content):
    # Find all test cases like PQ-TC-01, OQ-TC-01, etc.
    # We'll split the content by test case headers
    # A header usually looks like "1. PQ-TC-01: ..." or just "PQ-TC-01: ..."
    
    # Pattern to find TC headers
    pattern = r"([A-Z]Q-TC-\d+)"
    tcs = {}
    
    # Split content by the pattern, but keep the pattern
    parts = re.split(pattern, content)
    
    # parts[0] is everything before first TC
    # parts[1] is TC ID, parts[2] is its content, etc.
    for i in range(1, len(parts), 2):
        tc_id = parts[i]
        tc_content = parts[i+1] if i+1 < len(parts) else ""
        # Clean up tc_content until the next TC or major header
        # We'll just take everything until the next TC ID appears in parts
        tcs[tc_id] = tc_content
        
    return tcs

def format_new_tc_content(content):
    lines = content.splitlines()
    formatted = []
    for line in lines:
        l = line.strip()
        if not l: 
            formatted.append("")
            continue
        if l.startswith("Objective:") or l.startswith("Procedure:") or l.startswith("Acceptance Criteria:") or l.startswith("Results:"):
            formatted.append(f"**{l}**")
        elif l.startswith("-") or l.startswith("*") or re.match(r"^\d+\.", l):
            formatted.append(f"   {l}")
        else:
            # Likely a detail line, make it a bullet if it's not already
            if ":" not in l or len(l) > 50:
                formatted.append(f"   - {l}")
            else:
                formatted.append(f"   {l}")
    return "\n".join(formatted)

def refine_md_v2(old_content, new_content):
    # 1. Extract test cases from NEW content (the source of truth for procedures/results)
    new_tcs = extract_test_cases(new_content)
    
    # 2. Extract test cases from OLD content (to identify locations for replacement)
    # We want to replace the text between one TC header and the next.
    
    # We'll use a regex to replace content following a TC ID in the old file
    refined = old_content
    
    for tc_id, tc_data in new_tcs.items():
        # Clean the new data
        clean_data = format_new_tc_content(tc_data)
        
        # In the old content, find the TC ID and everything after it until the next TC or SECTION
        # We need to be careful not to match headers
        # Escaping tc_id for regex
        escaped_id = re.escape(tc_id)
        
        # This regex looks for tc_id, then non-greedy match until next tc_id or SECTION
        # We use (?ms) for dot-all and multi-line
        search_pattern = rf"({escaped_id}.*?)(?=\n\d+\. [A-Z]Q-TC-|\nSECTION|\n##|\Z)"
        
        # Check if it exists in old content
        match = re.search(search_pattern, refined, flags=re.DOTALL)
        if match:
            # Replace the content part. The match[1] includes the ID.
            # We want to keep the header of the TC from old version if possible (e.g. "1. PQ-TC-01: ...")
            # So we'll try to keep the first line of the match
            header_line = match.group(1).splitlines()[0]
            replacement = f"{header_line}\n{clean_data}\n"
            refined = refined.replace(match.group(1), replacement)
        else:
            # If TC ID not found in old, maybe it's a NEW test case?
            # We could append it to the end of the Test Result section, but let's skip for now
            # to maintain strict consistency unless the user wants more.
            pass
            
    return refined

root_dir = r"d:\ex_work\AirQualityReview_Project\validation_docs\csv_team_format"
appendices = [
    r"Appendix 1_FRA\Appendix 1_FRA.md",
    r"Appendix 2_Module\Appendix 2_Module.md",
    r"Appendix 3_Integration\Appendix 3_Integration.md",
    r"Appendix 4_Functional\Appendix 4_Functional.md",
    r"Appendix 5_Requirement\Appendix 5_Requirement.md"
]

for app_rel_path in appendices:
    full_path = os.path.join(root_dir, app_rel_path)
    print(f"Refining V2: {full_path}...")
    
    old_content = get_git_file(full_path)
    if not old_content:
        print(f"  Skipping {full_path}, old content not found in Git.")
        continue
        
    with open(full_path, "r", encoding="utf-8") as f:
        new_content = f.read()
        
    refined = refine_md_v2(old_content, new_content)
    
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(refined)
        
print("Refinement V2 complete.")
