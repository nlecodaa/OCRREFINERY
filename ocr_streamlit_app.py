import streamlit as st
import requests
import os
import tempfile
from fpdf import FPDF
import ocrmypdf
from ocrmypdf.exceptions import TaggedPDFError
from pathlib import Path
from llm_corrector_api import correct_ocr_text_togetherai

# --- Backend API Call ---
def call_backend_ocr_api(file_path):
    with open(file_path, 'rb') as f:
        files = {'file': f}
        try:
            response = requests.post("https://refinerybackend.onrender.com/ocr", files=files)
            response.raise_for_status()
            return response.json().get("text", "")
        except requests.exceptions.RequestException as e:
            st.error(f"Backend request failed: {e}")
            return ""

# --- PDF Font Support ---
def get_dejavu_font_path():
    font_dir = os.path.join(os.path.dirname(__file__), "fonts")
    font_path = os.path.join(font_dir, "DejaVuSans.ttf")
    if not os.path.exists(font_path):
        import urllib.request
        os.makedirs(font_dir, exist_ok=True)
        url = "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf"
        try:
            with st.spinner("Downloading Unicode font (DejaVu Sans)..."):
                urllib.request.urlretrieve(url, font_path)
        except Exception as e:
            st.warning("Could not download DejaVuSans.ttf. PDF export may fail for non-English text.")
            return None
    return font_path

def break_long_line(pdf, line, available_width):
    while line:
        segment = line
        while pdf.get_string_width(segment) > available_width and segment:
            segment = segment[:-1]
        if not segment:
            segment = line[0]
        pdf.cell(available_width, 10, segment, ln=1)
        line = line[len(segment):]

def save_text_to_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_left_margin(10)
    pdf.set_right_margin(10)
    available_width = pdf.w - pdf.l_margin - pdf.r_margin

    font_path = get_dejavu_font_path()
    font_loaded = False
    if font_path:
        try:
            pdf.add_font("DejaVu", "", font_path, uni=True)
            pdf.set_font("DejaVu", size=12)
            font_loaded = True
        except Exception as e:
            st.warning(f"Could not load DejaVu font: {e}. Falling back to Arial.")
    if not font_loaded:
        pdf.set_font("Arial", size=12)

    for line in text.split("\n"):
        pdf.set_x(pdf.l_margin)
        if not line.strip():
            pdf.ln(10)
            continue
        line_width = pdf.get_string_width(line)
        if line_width > available_width:
            try:
                pdf.multi_cell(available_width, 10, line)
            except Exception:
                break_long_line(pdf, line, available_width)
        else:
            pdf.cell(available_width, 10, line, ln=1)

    pdf_data = pdf.output(dest='S')
    if isinstance(pdf_data, str):
        pdf_data = pdf_data.encode('latin1')
    elif isinstance(pdf_data, bytearray):
        pdf_data = bytes(pdf_data)
    return pdf_data

def make_pdf_searchable(input_path, output_path, lang):
    try:
        ocrmypdf.ocr(input_path, output_path, language=lang)
        return True
    except TaggedPDFError:
        return "already_tagged"
    except Exception as e:
        return str(e)

# --- Custom CSS for Modern Look ---
st.markdown("""
    <style>
        .block-logo {
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 3rem;
            font-weight: 900;
            letter-spacing: 0.14em;
            color: #1976d2;
            text-align: center;
            margin-top: 10px;
            margin-bottom: 30px;
            text-shadow: 2px 2px 8px #e3e3e3;
        }
        .section-title {
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 1.5rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 20px;
            margin-top: 10px;
            color: #333;
        }
        .sidebar-content {
            background: linear-gradient(120deg, #f3f8ff 60%, #e3e6f3 100%);
            border-radius: 10px;
            padding: 14px;
            margin-bottom: 18px;
            border: 1px solid #e0e0e0;
        }
        .sidebar-link a {
            color: #1976d2 !important;
            text-decoration: none;
            font-weight: 600;
        }
    </style>
""", unsafe_allow_html=True)

# --- Branding ---
st.markdown('<div class="block-logo">🦾 OCR REFINERY Lite</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">OCR + LLM TEXT CLEANER</div>', unsafe_allow_html=True)

# --- Sidebar: Lightweight Notice, Links, Contact ---
st.sidebar.markdown("""
<div class="sidebar-content">
<b>🚦 Lightweight Version</b><br>
This is a <span style="color:#1976d2;"><b>lightweight</b></span> version of the main project.<br>
The backend is hosted on a <b>free server</b>, so performance may be limited.<br>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("""
- 🌟 <span class="sidebar-link">[Main Project GitHub](https://github.com/yourusername/yourproject)</span>
- 💬 Want to help expand or chase infinity?<br>
  <b>Contact:</b> <a href="mailto:yourmail@example.com">yourmail@example.com</a>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("""
- [LinkedIn](https://www.linkedin.com/in/nlecodaa)
- [GitHub](https://github.com/nlecodaa)
""")

# --- Main UI ---
uploaded_file = st.file_uploader("Upload an Image or PDF", type=["jpg", "jpeg", "png", "pdf"])
ocr_lang = st.selectbox("Select OCR Language", ["eng", "spa", "fra", "deu", "ita", "por", "rus", "chi_sim", "jpn"])

# --- Searchable PDF Button ---
if uploaded_file and uploaded_file.name.endswith(".pdf"):
    if st.button("🔍 Make PDF Searchable"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_input:
            temp_input.write(uploaded_file.getbuffer())
            temp_input_path = temp_input.name

        temp_output_path = temp_input_path.replace(".pdf", "_searchable.pdf")
        with st.spinner("Running OCR to add selectable text..."):
            result = make_pdf_searchable(temp_input_path, temp_output_path, ocr_lang)

        if result is True:
            with open(temp_output_path, "rb") as f:
                st.download_button("⬇️ Download Searchable PDF", f, file_name="searchable_output.pdf")
        elif result == "already_tagged":
            st.info("📄 This PDF already has selectable text.")
        else:
            st.error(f"Error: {result}")

# --- Main OCR + LLM Pipeline ---
if uploaded_file:
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        try:
            with st.spinner("Extracting text with OCR, please wait..."):
                progress_bar = st.progress(0)
                ocr_text = call_backend_ocr_api(file_path)
                progress_bar.progress(100)
        except Exception as e:
            st.error(f"OCR failed: {e}")
            st.stop()

        st.subheader("🖨️ Raw OCR Output")
        st.text_area("OCR Text", ocr_text, height=200, key="raw_ocr")

        if st.button("✨ Clean Text with LLM"):
            with st.spinner("Cleaning text with AI..."):
                progress_bar = st.progress(0)
                cleaned = correct_ocr_text_togetherai(ocr_text)
                progress_bar.progress(100)

            st.subheader("🧼 Cleaned OCR Output")
            st.text_area("✨ LLM Output", cleaned, height=300, key="cleaned_ocr")

            st.download_button(
                "Download Cleaned Text (.txt)",
                cleaned,
                file_name="cleaned_ocr.txt"
            )

            try:
                with st.spinner("Generating PDF..."):
                    pdf_bytes = save_text_to_pdf(cleaned)
                    st.download_button(
                        "Download Cleaned PDF",
                        pdf_bytes,
                        file_name="cleaned_ocr.pdf",
                        mime='application/pdf'
                    )
            except Exception as e:
                st.error(f"PDF generation failed: {e}")
                st.info("As a fallback, you can copy the text below:")
                st.code(cleaned)

# --- Info Section ---
st.header("About")
st.markdown("""
This app extracts text from images/PDFs using OCR, then refines the output using AI (LLM). 
Ideal for digitizing printed material with formatting and punctuation cleanup.
""")

st.header("Instructions / Step-by-Step Guide")
st.markdown("""
1. **Upload** an image or PDF  
2. *(Optional)* Make PDF searchable  
3. **Select language**  
4. **Extract OCR text**  
5. **Review and clean it with AI**  
6. **Download cleaned text or PDF**
""")