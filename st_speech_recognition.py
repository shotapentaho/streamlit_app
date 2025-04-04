import streamlit as st
import speech_recognition as sr

st.title("🎙️ Live Speech to Text")
st.write("Press the button to speak and transcribe your voice to text.")

if st.button("🎤 Start Recording"):
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        st.info("Speak now...")
        audio = recognizer.listen(source)

        try:
            st.success("✅ Transcription:")
            text = recognizer.recognize_google(audio)
            st.write(text)
        except sr.UnknownValueError:
            st.error("❌ Could not understand the audio.")
        except sr.RequestError:
            st.error("⚠️ Request to the recognition service failed.")
