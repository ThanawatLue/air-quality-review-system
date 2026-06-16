import os
import glob
import shutil

src_root = r"D:\ex_work\AirQualityReview_Project\data\CSV B.10 AQR"
dst_root = r"D:\ex_work\AirQualityReview_Project\data\CSV B.10 AQR_Fallback"

# Find all files with _fallback in the name under src_root recursively
pattern = os.path.join(src_root, "**", "*_fallback*")
fallback_files = glob.glob(pattern, recursive=True)

print(f"Found {len(fallback_files)} fallback files to move.")

for src_path in fallback_files:
    # Calculate relative path from src_root
    rel_path = os.path.relpath(src_path, src_root)
    # Calculate destination path
    dst_path = os.path.join(dst_root, rel_path)
    # Get destination directory
    dst_dir = os.path.dirname(dst_path)
    # Create destination directory if it doesn't exist
    os.makedirs(dst_dir, exist_ok=True)
    # Move the file
    shutil.move(src_path, dst_path)
    print(f"Moved: {rel_path} -> {dst_path}")

print("Done moving fallback files.")
