import os
import streamlit as st
import fitz  # PyMuPDF for PDF processing


# Ensure 'static/' directory exists
STATIC_DIR = "/tmp/static"
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

# Streamlit UI
st.title("📄 PDF Text Extractor")
# File uploader
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file:
    # Save PDF to 'static/' directory
    pdf_path = os.path.join(STATIC_DIR, uploaded_file.name)
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Open and extract text
    with fitz.open(pdf_path) as pdf:
        text = "\n\n".join(page.get_text() for page in pdf)

    # Display extracted text
    st.subheader("📜 Extracted Text:")
    st.text_area("", text, height=400)

    # Save extracted text as a file in 'static/'
    text_file_path = os.path.join(STATIC_DIR, "extracted_text.txt")
    with open(text_file_path, "w", encoding="utf-8") as text_file:
        text_file.write(text)

    # Option to download the extracted text
    st.download_button("📥 Download Extracted Text", text, file_name="extracted_text.txt")
