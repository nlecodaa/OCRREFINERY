from pdf2image import convert_from_path
pages = convert_from_path("sample.pdf", dpi=300, poppler_path=r"C:\poppler-24.08.0\Library\bin")
print(f"✅ {len(pages)} pages converted")