import os
import subprocess
import re

def get_git_file(file_path):
    git_path = file_path.replace("\\", "/")
    if "AirQualityReview_Project/" in git_path:
        git_path = git_path.split("AirQualityReview_Project/")[1]
    result = subprocess.run(["git", "show", f"HEAD:{git_path}"], capture_output=True, text=True, encoding="utf-8")
    return result.stdout if result.returncode == 0 else ""

def format_content(content):
    lines = content.splitlines()
    formatted = []
    tc_count = 0
    for line in lines:
        l = line.strip()
        if not l: 
            formatted.append("")
            continue
        if "-TC-" in l:
            tc_count += 1
            # Remove any existing numbers to re-number
            clean_tc = re.sub(r"^\d+\.?\s*", "", l)
            formatted.append(f"{tc_count}. {clean_tc}")
        elif l.startswith("Objective:") or l.startswith("Procedure:") or l.startswith("Acceptance Criteria:") or l.startswith("Results:"):
            formatted.append(f"**{l}**")
        elif l.startswith("-") or l.startswith("*") or l.startswith("•"):
            formatted.append(f"   {l}")
        elif re.match(r"^\d+\.", l): # Steps
            formatted.append(f"   {l}")
        else:
            formatted.append(f"   - {l}")
    return "\n".join(formatted)

def refine_md_v3(old_content, new_content):
    # Find SECTION 6 or TEST RESULT in both
    def find_test_range(content):
        lines = content.splitlines()
        start = -1
        for i, line in enumerate(lines):
            if "TEST RESULT" in line.upper():
                start = i
                break
        if start == -1: return None
        
        end = len(lines)
        for i in range(start + 1, len(lines)):
            if "SECTION" in lines[i].upper() and lines[i].strip():
                end = i
                break
        return start, end

    old_range = find_test_range(old_content)
    new_range = find_test_range(new_content)
    
    if not old_range or not new_range:
        return new_content # Fallback if structure is too different
        
    old_lines = old_content.splitlines()
    new_lines = new_content.splitlines()
    
    # Extract and format NEW test cases
    raw_new_test_content = "\n".join(new_lines[new_range[0]+1:new_range[1]])
    formatted_new_content = format_content(raw_new_test_content)
    
    # Reassemble
    final = old_lines[:old_range[0]+1]
    final.append(formatted_new_content)
    final.extend(old_lines[old_range[1]:])
    
    return "\n".join(final)

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
    print(f"Refining V3: {full_path}...")
    old_content = get_git_file(full_path)
    if not old_content: continue
    with open(full_path, "r", encoding="utf-8") as f:
        new_content = f.read()
    refined = refine_md_v3(old_content, new_content)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(refined)

print("Refinement V3 complete.")
