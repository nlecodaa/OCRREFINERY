from pdf_ocr import process_pdf
pdf_path = "sample.pdf"
output_path = "output/pdf_output.txt"
print("⚡ Running PDF OCR...")
process_pdf(pdf_path, output_path)