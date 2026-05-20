import os
import re

def fix_manuals():
    brain_manual = r"C:\Users\thana\.gemini\antigravity\brain\aa85b059-14a1-4288-a587-0cefeb8d2e06\AQR_User_Manual.md"
    
    if os.path.exists(brain_manual):
        print(f"Reading brain manual: {brain_manual}")
        with open(brain_manual, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Replace image links to use `./01_dashboard_initial.png` format (within artifact directory)
        pattern = r"\([^)]*?((?:0\d|analysis_flowchart)[^/]*?\.png)\)"
        
        def repl_func(match):
            filename = match.group(1)
            # Normalize to `./00_analysis_flowchart.png` or `./01_dashboard_initial.png`
            if "analysis_flowchart" in filename:
                return "(./00_analysis_flowchart.png)"
            return f"(./{filename})"
            
        new_content = re.sub(pattern, repl_func, content)
        
        if new_content != content:
            with open(brain_manual, "w", encoding="utf-8") as f:
                f.write(new_content)
            print("Successfully updated brain manual to relative within-artifact paths.")
        else:
            print("Brain manual image paths were already updated or no match found.")

if __name__ == "__main__":
    fix_manuals()

