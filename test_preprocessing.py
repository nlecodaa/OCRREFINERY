import cv2
import os
from preprocessor import process_file
input_path = "sample.jpg" 
try:
    text = process_file(input_path, save_preproc=True)
    print("✅ OCR Text Output:\n")
    print(text)
except FileNotFoundError as e:
    print(f"❌ Error: {e}")
    exit()
if input_path.lower().endswith('.pdf'):
    for i in range(1, 100):  
        img_name = f"{os.path.splitext(input_path)[0]}_page{i:03d}.png"
        if os.path.exists(img_name):
            img = cv2.imread(img_name)
            cv2.imshow(f"Page {i}", img)
        else:
            break
else:
    img_name = f"{os.path.splitext(input_path)[0]}_prep.png"
    if os.path.exists(img_name):
        img = cv2.imread(img_name)
        cv2.imshow("Processed Image", img)
cv2.waitKey(0)
cv2.destroyAllWindows()