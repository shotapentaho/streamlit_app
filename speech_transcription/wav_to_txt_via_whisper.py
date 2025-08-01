import streamlit as st
import openai

st.title("Vonage WAV File Converter")
st.write(
    """
    Upload your Vonage .wav call recording and get an instant transcription using OpenAI Whisper.
    """
)

openai.api_key = st.secrets["openai"]["api_key"]

uploaded_file = st.file_uploader("Upload audio file", type=["wav", "mp3", "m4a"])

if uploaded_file:
    st.audio(uploaded_file)
    with st.spinner("Transcribing..."):
        audio_bytes = uploaded_file.read()
        response = openai.audio.transcriptions.create(
            model="whisper-1",
            file=(uploaded_file.name, audio_bytes)
        )
        st.write("Transcription:")
        st.write(response.text)