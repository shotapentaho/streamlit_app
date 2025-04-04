import streamlit as st
import tensorflow as tf
import numpy as np
from PIL import Image
import requests
from io import BytesIO

# Load the pre-trained MobileNetV2 model
model = tf.keras.applications.MobileNetV2(weights="imagenet")

# Load ImageNet labels
LABELS_URL = "https://storage.googleapis.com/download.tensorflow.org/data/imagenet_class_index.json"
labels = requests.get(LABELS_URL).json()
imagenet_labels = {int(k): v[1] for k, v in labels.items()}

# Streamlit UI
st.title("🖼️ Image Recognition with MobileNetV2")
st.write("Upload an image and let the AI predict what it is!")

# File uploader
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # Open and display image
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # Preprocess image for MobileNetV2
    image = image.resize((224, 224))  # Resize to 224x224
    image_array = np.array(image) / 255.0  # Normalize pixel values
    image_array = np.expand_dims(image_array, axis=0)  # Add batch dimension

    # Predict using the model
    predictions = model.predict(image_array)
    top_3_indices = np.argsort(predictions[0])[-3:][::-1]  # Top 3 predictions

    # Display predictions
    st.write("### 🎯 Predictions:")
    for i in top_3_indices:
        label = imagenet_labels[i]
        confidence = predictions[0][i] * 100
        st.write(f"✅ **{label.capitalize()}** - {confidence:.2f}% confidence")
