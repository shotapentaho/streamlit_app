import streamlit as st
import whisper
import tempfile
import os

st.title("WAV to Text Transcription (OpenAI Whisper)")

uploaded_file = st.file_uploader("Upload a WAV file", type=["wav"])

if uploaded_file is not None:
    # Save the uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
        tmpfile.write(uploaded_file.read())
        tmp_path = tmpfile.name

    st.info("Transcribing... This may take a moment.")

    # Load Whisper model (change to "medium" or "large" for better accuracy if you wish)
    model = whisper.load_model("base")
    result = model.transcribe(tmp_path)

    st.success("Transcription complete!")
    st.markdown("#### Transcribed Text:")
    st.write(result["text"])

    # Clean up temp file
    os.remove(tmp_path)