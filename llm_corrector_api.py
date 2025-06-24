import requests
import os

TOGETHER_API_KEY = "tgp_v1_Xn0QY1s8UYeqmkKhLuFNPy-HPTirft9lsZYPOBulY7Y"

def correct_ocr_text_togetherai(ocr_text, model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"):
    url = "https://api.together.xyz/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are an OCR cleanup assistant. Clean up the following text: fix formatting, punctuation, remove OCR noise, and make it easy to read."},
            {"role": "user", "content": ocr_text}
        ],
        "temperature": 0.3,
        "max_tokens": 1024
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]
