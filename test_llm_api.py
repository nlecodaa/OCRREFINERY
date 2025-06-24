from llm_corrector_api import correct_ocr_text_togetherai
with open("output/tesseract_output.txt", "r", encoding="utf-8") as f:
    ocr_raw = f.read()
cleaned = correct_ocr_text_togetherai(ocr_raw)
with open("output/tesseract_cleaned_llm.txt", "w", encoding="utf-8") as f:
    f.write(cleaned)
print("✅ Cleaned OCR saved to output/tesseract_cleaned_llm.txt")
