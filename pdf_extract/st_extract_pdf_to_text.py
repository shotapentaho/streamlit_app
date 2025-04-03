import os
import streamlit as st
import fitz  # PyMuPDF for PDF processing


# Ensure the 'static/' directory exists 
if not os.path.exists("static"):
    os.makedirs("static")

# Streamlit UI
st.title("📄 PDF Text Extractor")

# File uploader
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file:
    # Open the PDF file
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as pdf:
        text = ""
        for page in pdf:
            text += page.get_text() + "\n\n"

    # Display extracted text
    st.subheader("📜 Extracted Text:")
    st.text_area("", text, height=400)

    # Option to download the extracted text
    st.download_button("📥 Download Text", text, file_name="extracted_text.txt")
