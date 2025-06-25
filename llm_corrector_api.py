import requests
import streamlit as st

# Securely access the Together API key from Streamlit secrets
TOGETHER_API_KEY = st.secrets["TOGETHER_API_KEY"]

def correct_ocr_text_togetherai(ocr_text, model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"):
    """
    Cleans OCR text using Together AI's LLM. Improves punctuation, formatting, and readability.

    Args:
        ocr_text (str): Raw OCR output to be cleaned.
        model (str): The Together AI model to use (default is Llama 3.3 70B Instruct).

    Returns:
        str: Cleaned and readable version of the input OCR text.
    """
    url = "https://api.together.xyz/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": (
                "You are an OCR cleanup assistant. "
                "Your job is to clean up scanned text extracted using OCR. "
                "Fix formatting, punctuation, spacing, remove OCR artifacts (like §, ;|, ., ..), "
                "correct common misspellings, and make the text easier to read."
            )},
            {"role": "user", "content": ocr_text}
        ],
        "temperature": 0.3,
        "max_tokens": 1024
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        st.error(f"⚠️ LLM Correction failed: {e}")
        return ocr_text 