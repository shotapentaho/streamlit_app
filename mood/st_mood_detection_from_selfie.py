import streamlit as st
import cv2
import numpy as np
from deepface import DeepFace
from PIL import Image

# Streamlit Title
st.title("📸 Mood Detection from Selfie")

# File Uploader for Selfie
uploaded_file = st.file_uploader("Upload a selfie", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Convert to OpenCV format
    image = Image.open(uploaded_file)
    image_np = np.array(image)
    
    # Convert to BGR format for OpenCV processing
    image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
    
    # Display uploaded image
    st.image(image, caption="Uploaded Selfie", use_container_width=True)

    # Analyze Mood using DeepFace
    with st.spinner("Analyzing mood..."):
        try:
            result = DeepFace.analyze(image_bgr, actions=["emotion"], enforce_detection=False)
            mood = result[0]['dominant_emotion']  # Get dominant emotion
            st.success(f"😃 Detected Mood: **{mood.capitalize()}**")
        except Exception as e:
            st.error(f"Error in mood detection: {e}")
