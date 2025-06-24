import os
import cv2
from preprocessor import preprocess_image
from ocr_engine import extract_text_tesseract
from pdf2image import convert_from_path

POPPLER_PATH = r"C:\poppler-24.08.0\Library\bin" 

def process_image_file(img_path):
    img = preprocess_image(img_path)
    text = extract_text_tesseract(img)
    return text
def process_pdf_file(pdf_path):
    pages = convert_from_path(pdf_path, dpi=300, poppler_path=POPPLER_PATH)
    all_text = ""
    for i, page in enumerate(pages):
        temp_img = f"temp_page_{i+1}.jpg"
        page.save(temp_img, "JPEG")
        processed = preprocess_image(temp_img)
        text = extract_text_tesseract(processed)
        all_text += f"\n--- Page {i+1} ---\n{text}"
        os.remove(temp_img)
    return all_text
def batch_process(input_dir="input", output_dir="output"):
    os.makedirs(output_dir, exist_ok=True)
    for file in os.listdir(input_dir):
        path = os.path.join(input_dir, file)
        name, ext = os.path.splitext(file)
        try:
            if ext.lower() in [".jpg", ".jpeg", ".png"]:
                print(f"📷 Processing image: {file}")
                result = process_image_file(path)
            elif ext.lower() == ".pdf":
                print(f"📄 Processing PDF: {file}")
                result = process_pdf_file(path)
            else:
                print(f"❌ Skipped unsupported file: {file}")
                continue
            with open(os.path.join(output_dir, f"{name}_ocr.txt"), "w", encoding="utf-8") as f:
                f.write(result)
            print(f"✅ Done: {file}")
        except Exception as e:
            print(f"⚠️ Failed on {file}: {e}")