import streamlit as st
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from PIL import Image

# Load the pre-trained model (replace with your model)
@st.cache_resource
def load_model():
    return tf.keras.models.load_model("bone_fracture_model.h5")

model = load_model()

# Function to process image and make prediction
def predict_bone_fracture(img):
    img = img.resize((224, 224))  # Resize to match model input
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    img_array = img_array / 255.0  # Normalize

    prediction = model.predict(img_array)[0]
    return prediction  # Assuming output is [fracture_prob, normal_prob]

# Streamlit UI
st.title("🔍 Bone Fracture Detection")

uploaded_file = st.file_uploader("Upload an X-ray Image", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="Uploaded Image", use_column_width=True)

    st.write("⏳ Analyzing...")

    prediction = predict_bone_fracture(img)
    
    fracture_prob = prediction[0]  # Assuming first output is fracture probability
    normal_prob = prediction[1]

    if fracture_prob > normal_prob:
        st.error(f"🚨 Fracture Detected! (Confidence: {fracture_prob:.2%})")
    else:
        st.success(f"✅ No Fracture Detected (Confidence: {normal_prob:.2%})")
