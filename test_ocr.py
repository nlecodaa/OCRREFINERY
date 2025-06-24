import cv2
import os
from preprocessor import preprocess_image
from ocr_engine import extract_text_tesseract, extract_text_easyocr
image_path = "sample.jpg"
output_folder = "output"
processed_image = preprocess_image(image_path)
print("\n🖨️ Printed Text OCR Output:")
text_tesseract = extract_text_tesseract(processed_image)
print(text_tesseract)
with open(os.path.join(output_folder, "tesseract_output.txt"), "w", encoding="utf-8") as f:
    f.write(text_tesseract)
print("\n✍️ Handwritten Text OCR Output:")
text_easyocr = extract_text_easyocr(image_path)
print(text_easyocr)
with open(os.path.join(output_folder, "easyocr_output.txt"), "w", encoding="utf-8") as f:
    f.write(text_easyocr)