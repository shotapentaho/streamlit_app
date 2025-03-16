import streamlit as st
from googletrans import Translator, LANGUAGES

# Initialize Translator
translator = Translator()

# Streamlit App Title
st.title("🌍 Language Translator")

# Input text box
text = st.text_area("Enter text to translate:")

# Language Selection
col1, col2 = st.columns(2)

with col1:
    src_lang = st.selectbox("Select source language:", ["auto"] + list(LANGUAGES.values()))

with col2:
    dest_lang = st.selectbox("Select target language:", list(LANGUAGES.values()), index=list(LANGUAGES.values()).index("english"))

# Translation Button
if st.button("Translate"):
    if text.strip():
        # Get language codes
        src_code = [code for code, lang in LANGUAGES.items() if lang == src_lang] or ["auto"]
        dest_code = [code for code, lang in LANGUAGES.items() if lang == dest_lang][0]

        # Translate text
        translation = translator.translate(text, src=src_code[0], dest=dest_code)

        # Display Result
        st.subheader("Translated Text:")
        st.write(translation.text)
    else:
        st.warning("Please enter text to translate.")

# Footer
st.markdown("Powered by Google Translate API 🌎")
