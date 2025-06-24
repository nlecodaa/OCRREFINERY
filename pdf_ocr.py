import os
import cv2
from pdf2image import convert_from_path
from preprocessor import preprocess_image
from ocr_engine import extract_text_tesseract


POPPLER_PATH = r"C:\poppler-24.08.0\Library\bin" 
def process_pdf(pdf_path, output_txt_path):
    pages = convert_from_path(pdf_path, dpi=300, poppler_path=POPPLER_PATH)
    print(f"✅ {len(pages)} pages detected")
    all_text = ""
    for i, page in enumerate(pages):
         print(f"🔄 Processing page {i+1}...")
    image_path = f"page_{i+1}.jpg"
    page.save(image_path, "JPEG")
    processed = preprocess_image(image_path)
    text = extract_text_tesseract(processed)
    all_text += f"\n\n--- Page {i+1} ---\n{text}"
    os.remove(image_path)
    os.makedirs("output", exist_ok=True)
    with open(output_txt_path, "w", encoding="utf-8") as f:
        f.write(all_text)
    print(f"✅ Done! Output saved to: {output_txt_path}")