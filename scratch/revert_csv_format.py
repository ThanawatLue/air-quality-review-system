import os
import glob
import re
import math
from datetime import datetime

def format_datetime(dt_str):
    dt_str = dt_str.strip().strip('"').strip("'")
    for fmt in ["%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%m/%d/%Y %H:%M:%S", "%m/%d/%Y %H:%M"]:
        try:
            dt = datetime.strptime(dt_str, fmt)
            # Desigo CC format: DD/MM/YYYY H:MM:SS (single-digit hour)
            return f"{dt.day:02d}/{dt.month:02d}/{dt.year} {dt.hour}:{dt.minute:02d}:{dt.second:02d}"
        except ValueError:
            pass
    return dt_str

def to_desigo_scientific(val_str):
    val_str = val_str.strip().strip('"').strip("'")
    if not val_str:
        return ""
    # If already in scientific notation, return as is (but uppercase)
    if 'E' in val_str or 'e' in val_str:
        return val_str.upper()
    try:
        val_float = float(val_str)
    except ValueError:
        return val_str # Return non-numeric strings as is (e.g. xxxxxxxxxxxxxxxxxxx)

    if val_float == 0.0:
        return "0.0E+0"

    # Count significant digits to preserve original decimal precision
    # Remove sign, decimal point, and leading zeros
    s_clean = re.sub(r'[^0-9]', '', val_str).lstrip('0')
    if not s_clean:
        return "0.0E+0"

    sig_digits = len(s_clean)
    dp = sig_digits - 1

    # Calculate exponent
    val_abs = abs(val_float)
    e = int(math.floor(math.log10(val_abs)))
    
    # Calculate coefficient
    c_val = val_float / (10**e)
    c_val = round(c_val, dp)

    sign_str = "-" if val_float < 0 else ""
    c_str = f"{abs(c_val):.{dp}f}"
    exp_sign = "+" if e >= 0 else "-"
    exp_val = abs(e)

    return f"{sign_str}{c_str}E{exp_sign}{exp_val}"

def clean_line_delimiters(line, delimiter):
    # Remove trailing delimiters and newline
    line = line.strip()
    while line.endswith(delimiter):
        line = line[:-1].strip()
    return line

def process_csv_file(fpath):
    print(f"Processing: {fpath}")
    
    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
        raw_lines = f.readlines()

    # Determine delimiter in line 5
    line5 = raw_lines[4] if len(raw_lines) > 4 else ""
    delimiter = ";" if ";" in line5 else ","

    output_lines = []
    
    # Process Header (Lines 1-4)
    for i in range(min(4, len(raw_lines))):
        cleaned_h = clean_line_delimiters(raw_lines[i], delimiter)
        # Remove any surrounding double quotes if they were added
        if cleaned_h.startswith('"') and cleaned_h.endswith('"'):
            cleaned_h = cleaned_h[1:-1].strip()
        output_lines.append(cleaned_h)

    # Line 5: Column Headers
    output_lines.append("DateTime;Data Source;Value;Alias")

    # Process Data and Footer Lines
    for line in raw_lines[5:]:
        line_str = line.strip()
        if not line_str:
            output_lines.append("")
            continue
            
        # Check if it's a data line (starts with a date)
        # E.g. "1/6/2026 0:00" or "01/06/2026 0:00:00"
        # We split by the detected delimiter
        parts = [p.strip().strip('"').strip("'") for p in line_str.split(delimiter)]
        
        first_col = parts[0] if parts else ""
        is_data = bool(re.match(r'^\s*\d{1,2}/\d{1,2}/\d{4}', first_col))
        
        if is_data:
            # Pad or truncate parts to exactly 4 columns
            cols = (parts + ["", "", "", ""])[:4]
            col0 = format_datetime(cols[0])
            col1 = cols[1]
            col2 = to_desigo_scientific(cols[2])
            col3 = cols[3]
            
            # Semicolon joined
            data_row = f"{col0};{col1};{col2};{col3}"
            output_lines.append(data_row)
        else:
            # Footer / Remark lines
            cleaned_footer = clean_line_delimiters(line_str, delimiter)
            output_lines.append(cleaned_footer)

    # Write output to next to original file with _fallback appended
    base, ext = os.path.splitext(fpath)
    output_fpath = f"{base}_fallback{ext}"
    
    # Save the file with original encoding
    with open(output_fpath, 'w', newline='', encoding='utf-8') as f:
        f.write("\n".join(output_lines) + "\n")
        
    print(f"  Saved to: {output_fpath}")

def main():
    search_path = r"D:\ex_work\AirQualityReview_Project\data\CSV B.10 AQR\**\*.csv"
    files = glob.glob(search_path, recursive=True)
    
    processed_count = 0
    for fpath in files:
        # Skip fallback files
        if "_fallback" in fpath.lower():
            continue
        process_csv_file(fpath)
        processed_count += 1
        
    print(f"\nDone! Processed {processed_count} files.")

if __name__ == "__main__":
    main()
