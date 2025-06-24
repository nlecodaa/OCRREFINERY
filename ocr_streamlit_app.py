import streamlit as st
from llm_corrector_api import correct_ocr_text_togetherai
from preprocessor import process_file
import os
import tempfile
from fpdf import FPDF
import ocrmypdf
from ocrmypdf.exceptions import TaggedPDFError
from pathlib import Path


def get_dejavu_font_path():
    """Ensure DejaVuSans.ttf exists in ./fonts/ and return its path. Download if missing."""
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
    """Break unbreakably long lines into chunks that fit in the available width"""
    while line:
        segment = line
        while pdf.get_string_width(segment) > available_width and segment:
            segment = segment[:-1]
        if not segment:
            segment = line[0]
        pdf.cell(available_width, 10, segment, ln=1)
        line = line[len(segment):]

def save_text_to_pdf(text):
    """Convert text to PDF with Unicode support (DejaVu Sans) and fallback. Always return bytes."""
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

    # Ensure return type is always bytes, never bytearray or str
    pdf_data = pdf.output(dest='S')
    if isinstance(pdf_data, str):
        pdf_data = pdf_data.encode('latin1')
    elif isinstance(pdf_data, bytearray):
        pdf_data = bytes(pdf_data)
    # else, already bytes
    return pdf_data


st.markdown("""
    <style>
    .block-logo {
        font-family: 'Helvetica Neue', Arial, 'Segoe UI', sans-serif;
        font-size: 3.2rem;
        font-weight: 900;
        letter-spacing: 0.18em;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 28px;
    }
    .section-title {
        font-family: 'sans-serif', Arial;
        font-size: 1.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 18px;
        margin-top: 8px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="block-logo">OCR REFINERY</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">OCR + LLM TEXT CLEANER</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload an Image or PDF", type=["jpg", "jpeg", "png", "pdf"])
ocr_lang = st.selectbox("Select OCR Language", ["eng", "spa", "fra", "deu", "ita", "por", "rus", "chi_sim", "jpn"])

st.sidebar.title("Contact & Info")
st.sidebar.markdown("""
- [LinkedIn](https://www.linkedin.com/in/nlecodaa)
- [GitHub](https://github.com/nlecodaa)
- Email: [nlecodaa@gmail.com](mailto:nlecodaa@gmail.com)
- Need custom help? [Email me](mailto:nlecodaa@gmail.com?subject=Custom%20Help%20Request)

---

## Changelog
- v1.0: Initial release with OCR and LLM text cleaning
- v1.1: Added progress bar, language selection, theme switcher, and contact info
- v1.2: Fixed PDF generation issues with long lines and unbreakable words
- v1.3: Added Unicode font support for international characters
""")
st.sidebar.markdown("---")
st.sidebar.markdown("**Analytics:** Coming soon...")

def make_pdf_searchable(input_path, output_path):
    try:
        ocrmypdf.ocr(input_path, output_path, language=ocr_lang)
        return True
    except TaggedPDFError:
        return "already_tagged"
    except Exception as e:
        return str(e)

if uploaded_file and uploaded_file.name.endswith(".pdf"):
    if st.button("🔍 Make PDF Searchable"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_input:
            temp_input.write(uploaded_file.getbuffer())
            temp_input_path = temp_input.name

        temp_output_path = temp_input_path.replace(".pdf", "_searchable.pdf")

        with st.spinner("Running OCR to add selectable text..."):
            result = make_pdf_searchable(temp_input_path, temp_output_path)

        if result is True:
            with open(temp_output_path, "rb") as f:
                st.download_button("⬇️Download Searchable PDF", f, file_name="searchable_output.pdf")
        elif result == "already_tagged":
            st.info("📄 This PDF already has selectable text. No need to OCR it again.")
        else:
            st.error(f"Error: {result}")

if uploaded_file:
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        try:
            with st.spinner("Extracting text with OCR, please wait..."):
                progress_bar = st.progress(0)
                ocr_text = process_file(file_path, lang=ocr_lang, save_preproc=False)
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
                st.error("Please try with a smaller document or contact support")
                st.info("As a fallback, you can copy the text below:")
                st.code(cleaned)

st.header("About")
st.markdown("""
This application is designed to help users extract, clean, and export text from images and PDF files with high accuracy and efficiency. By combining advanced OCR technology with AI-based text correction, the app transforms scanned documents into readable, editable, and shareable digital text. It is ideal for students, professionals, and anyone needing to digitize printed materials.
""")

st.header("Instructions / Step-by-Step Guide")
st.markdown("""
1. **Upload** your file (JPG, JPEG, PNG, or PDF)
2. *(Optional)* Make PDF searchable if applicable
3. **Select OCR language**
4. **Extract text** with progress bar
5. **Review raw OCR output**
6. **Clean text with AI**
7. **Download cleaned text** as .txt or .pdf
""")