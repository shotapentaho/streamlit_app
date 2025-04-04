import streamlit as st
import speechrecognition as sr

# Function to capture and recognize speech
def recognize_speech():
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        st.write("Please speak...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        
        try:
            st.write("Recognizing...")
            # Using Google Web Speech API for recognition
            text = recognizer.recognize_google(audio)
            st.write(f"Recognized Text: {text}")
        except sr.UnknownValueError:
            st.write("Sorry, I could not understand the audio.")
        except sr.RequestError as e:
            st.write(f"Could not request results from Google Speech Recognition service; {e}")

# Streamlit UI
st.title("Speech Recognition App")
st.write("Click the button to start speaking")

if st.button("Start Listening"):
    recognize_speech()
