import streamlit as st
from deep_translator import GoogleTranslator

# Streamlit App Title
st.title("🌍 Language Translator")

# Input text box
text = st.text_area("Enter text to translate:")

# Language Selection
languages = GoogleTranslator().get_supported_languages()

col1, col2 = st.columns(2)

with col1:
    src_lang = st.selectbox("Select source language:", ["auto"] + languages)

with col2:
    dest_lang = st.selectbox("Select target language:", languages, index=languages.index("english"))

# Translation Button
if st.button("Translate"):
    if text.strip():
        translation = GoogleTranslator(source=src_lang, target=dest_lang).translate(text)
        
        # Display Result
        st.subheader("Translated Text:")
        st.write(translation)
    else:
        st.warning("Please enter text to translate.")

st.markdown("Powered by Google Translate API 🌎")
