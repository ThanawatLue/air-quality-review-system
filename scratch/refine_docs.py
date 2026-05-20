import os
import subprocess

def get_git_file(file_path):
    # Normalize path for git (use forward slashes)
    git_path = file_path.replace("\\", "/")
    # Remove leading drive and project root if needed
    if "AirQualityReview_Project/" in git_path:
        git_path = git_path.split("AirQualityReview_Project/")[1]
    
    result = subprocess.run(["git", "show", f"HEAD:{git_path}"], capture_output=True, text=True, encoding="utf-8")
    if result.returncode == 0:
        return result.stdout
    else:
        # Try without encoding if it fails
        result = subprocess.run(["git", "show", f"HEAD:{git_path}"], capture_output=True, text=True)
        return result.stdout

def refine_md(old_content, new_content):
    # This is a heuristic approach. 
    # We want to keep the metadata and sections of old_content,
    # but replace the Test Result details with new_content.
    
    old_lines = old_content.splitlines()
    new_lines = new_content.splitlines()
    
    # Identify the Test Result section in both
    old_test_start = -1
    for i, line in enumerate(old_lines):
        if "SECTION 6: TEST RESULT" in line.upper() or "TEST RESULT" in line.upper():
            old_test_start = i
            break
            
    if old_test_start == -1:
        return new_content # Fallback
        
    # We'll keep everything before old_test_start from old_content
    final_lines = old_lines[:old_test_start + 1]
    
    # Now find where the Test Result ends in old_content (e.g., next SECTION)
    old_test_end = len(old_lines)
    for i in range(old_test_start + 1, len(old_lines)):
        if "SECTION" in old_lines[i].upper() and old_lines[i].strip():
            old_test_end = i
            break
            
    # Extract the "Actual" test results from new_content
    # The new_content was generated with "# From file.docx" headers.
    # We want to find the part after "## TEST RESULT" or similar.
    new_test_start = -1
    for i, line in enumerate(new_lines):
        if "TEST RESULT" in line.upper():
            new_test_start = i
            break
            
    if new_test_start == -1:
        # Just use the whole new content after headers
        for i, line in enumerate(new_lines):
            if not line.startswith("# From") and line.strip():
                new_test_start = i
                break
    
    # Process new lines to add bullets/numbers
    # Many lines in new_content are procedures that should be bullets.
    refined_new_lines = []
    tc_count = 0
    for line in new_lines[new_test_start:]:
        if line.strip().startswith("---"): continue
        if line.startswith("# From"): continue
        
        # Detect Test Case headers
        if "-TC-" in line:
            tc_count += 1
            refined_new_lines.append(f"\n{tc_count}. {line.strip()}")
        elif "Procedure:" in line or "Objective:" in line or "Acceptance Criteria:" in line or "Results:" in line:
            refined_new_lines.append(f"\n**{line.strip()}**")
        elif line.strip() and not line.startswith("|") and not line.startswith("#"):
            # It's likely a step or description
            refined_new_lines.append(f"   - {line.strip()}")
        else:
            refined_new_lines.append(line)
            
    final_lines.extend(refined_new_lines)
    
    # Append the rest of the old content (after Test Result section)
    final_lines.extend(old_lines[old_test_end:])
    
    return "\n".join(final_lines)

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
    print(f"Refining {full_path}...")
    
    old_content = get_git_file(full_path)
    with open(full_path, "r", encoding="utf-8") as f:
        new_content = f.read()
        
    refined = refine_md(old_content, new_content)
    
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(refined)
        
print("Refinement complete.")
