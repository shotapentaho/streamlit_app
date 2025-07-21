import streamlit as st
import openai
#from pytube import YouTube
from yt_dlp import YoutubeDL
from faster_whisper import WhisperModel
import os
import toml

st.set_page_config(layout="wide")
st.title("🎙️ YouTube Podcast Summarizer")

# Load secrets from .streamlit/secrets.toml
#secrets_path = os.path.join(os.path.dirname(__file__), ".streamlit", "secrets.toml")
#secrets = toml.load(secrets_path)
openai_api_key = st.secrets["openai"]["api_key"]
openai_client = openai.OpenAI(api_key=openai_api_key)

def download_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'audio.%(ext)s',
        # REMOVE postprocessors!
        'quiet': True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def transcribe_audio(file_path):
    model = WhisperModel("base")
    segments, _ = model.transcribe(file_path)
    return " ".join([seg.text for seg in segments])

def summarize_text(text):
    prompt = f"Summarize the following podcast:\n\n{text}"
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content

youtube_url = st.text_input("Enter YouTube URL:", value="https://www.youtube.com/watch?v=abc123")
if st.button("Summarize Podcast"):
    if youtube_url.strip():
        with st.spinner("Downloading audio..."):
            try:
                download_audio(youtube_url)
            except Exception as e:
                st.error(f"Audio download failed: {e}")
                st.stop()

        audio_file = "audio.mp3"
        if not os.path.exists(audio_file):
            files = [f for f in os.listdir('.') if f.startswith('audio.')]
            if files:
                audio_file = files[0]
            else:
                st.error("Audio file not found after download.")
                st.stop()

        with st.spinner("Transcribing audio..."):
            try:
                transcript = transcribe_audio(audio_file)
            except Exception as e:
                st.error(f"Transcription failed: {e}")
                st.stop()

        st.subheader("Transcript (first 1000 chars):")
        st.write(transcript[:1000] + "..." if len(transcript) > 1000 else transcript)

        with st.spinner("Summarizing..."):
            try:
                summary = summarize_text(transcript)
            except Exception as e:
                st.error(f"Summarization failed: {e}")
                st.stop()

        st.success("Summary:")
        st.write(summary)