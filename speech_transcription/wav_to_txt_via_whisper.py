import streamlit as st
import openai

openai.api_key = st.secrets["openai"]["api_key"] 
uploaded_file = st.file_uploader("Upload audio file", type=["wav", "mp3", "m4a"])

if uploaded_file:
    st.audio(uploaded_file)
    with st.spinner("Transcribing..."):
        response = openai.audio.transcribe(
            file=uploaded_file,
            model="whisper-1"
        )
        st.write("Transcription:")
        st.write(response["text"])