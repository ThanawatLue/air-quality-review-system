import fitz
import pytesseract
from PIL import Image
import io

pdf_path = r'D:\ex_work\gpo_AirQualityReview_Project\data\B16_2026-06-26\163-AHU03\16-3-047\Trends\16-3-047_RMT_2026-06-27_08-25-52-951_1.Pdf'
doc = fitz.open(pdf_path)
page = doc[0]

# Render page to image
pix = page.get_pixmap(dpi=300)
img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

# Crop the bottom half where the table usually is
width, height = img.size
cropped = img.crop((0, int(height * 0.5), width, int(height * 0.7)))

# Save cropped image for debugging
cropped.save("debug_crop.png")

# Extract text using Tesseract
text = pytesseract.image_to_string(cropped)
print("Extracted Text:")
print(text)
