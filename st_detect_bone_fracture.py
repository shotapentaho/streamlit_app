import streamlit as st
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, BatchNormalization
from PIL import Image


# Simple CNN Model
#model = Sequential([
#    Conv2D(32, (3,3), activation='relu', input_shape=(224, 224, 3)),
#    MaxPooling2D(2,2),
#    Flatten(),
#    Dense(128, activation='relu'),
#    Dense(2, activation='softmax')  # 2 classes: Fracture vs Normal
#])

# Improved CNN Model
model = Sequential([
    Conv2D(32, (3,3), activation='relu', input_shape=(224, 224, 3)),
    BatchNormalization(),  # Normalize activations
    MaxPooling2D(2,2),

    Conv2D(64, (3,3), activation='relu'),
    BatchNormalization(),
    MaxPooling2D(2,2),

    Conv2D(128, (3,3), activation='relu'),
    BatchNormalization(),
    MaxPooling2D(2,2),

    Flatten(),
    Dense(256, activation='relu'),
    Dropout(0.5),  # Helps prevent overfitting

    Dense(128, activation='relu'),
    Dropout(0.3),

    Dense(2, activation='softmax')  # 2 classes: Fracture vs Normal
])


# Compile Model, Save Model
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
model.save("bone_fracture_model.keras")

# Load the pre-trained model (replace with your model)
@st.cache_resource
def load_model():
    return tf.keras.models.load_model("bone_fracture_model.keras")

model = load_model()

# Function to process image and make prediction
def predict_bone_fracture(img):
    img = img.convert("RGB")  # Convert RGBA to RGB
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
    st.image(img, caption="Uploaded Image", use_container_width =True)

    st.write("⏳ Analyzing...")

    prediction = predict_bone_fracture(img)
    
    fracture_prob = prediction[0]  # Assuming first output is fracture probability
    normal_prob = prediction[1]
    st.write("Fracture Probability", fracture_prob)
    st.write("Normal Probability", normal_prob)
    if fracture_prob > normal_prob:
        st.error(f"🚨 Fracture Detected! (Confidence: {fracture_prob:.2%})")
    else:
        st.success(f"✅ No Fracture Detected (Confidence: {normal_prob:.2%})")
