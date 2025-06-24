import os
import cv2
import fitz  
import numpy as np
import pytesseract
import argparse

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def pdf_page_to_image(page, dpi=300):
    matrix = fitz.Matrix(dpi / 72, dpi / 72)
    pix = page.get_pixmap(matrix=matrix, colorspace=fitz.csRGB)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
    return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

def preprocess(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return th

def ocr(img, lang='eng', psm=6, oem=3):
    config = f'--oem {oem} --psm {psm}'
    return pytesseract.image_to_string(img, lang=lang, config=config)

def process_file(path, lang='eng', save_preproc=False):
    texts = []
    base, ext = os.path.splitext(path)
    if ext.lower() == '.pdf':
        doc = fitz.open(path)
        for i, page in enumerate(doc, 1):
            img = pdf_page_to_image(page)
            prep = preprocess(img)
            if save_preproc:
                out_path = f"{base}_page{i:03d}_prep.png"
                cv2.imwrite(out_path, prep)
            texts.append(ocr(prep, lang))
    else:
        img = cv2.imread(path)
        if img is None:
            raise FileNotFoundError(f'Could not read image: {path}')
        prep = preprocess(img)
        if save_preproc:
            out_path = f"{base}_prep.png"
            cv2.imwrite(out_path, prep)
        texts.append(ocr(prep, lang))
    return '\n'.join(texts)

def main():
    ap = argparse.ArgumentParser(description='Minimal OCR pipeline for images and PDFs')
    ap.add_argument('input', help='PDF or image file')
    ap.add_argument('-l', '--lang', default='eng', help='Tesseract language(s), e.g. "eng+deu"')
    ap.add_argument('-o', '--output', help='Optional output text file')
    ap.add_argument('--save-preproc', action='store_true', help='Save preprocessed images')
    args = ap.parse_args()

    text = process_file(args.input, args.lang, args.save_preproc)
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(text)
    else:
        print(text)

if __name__ == '__main__':
    main()
