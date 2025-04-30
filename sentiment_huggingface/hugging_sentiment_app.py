import streamlit as st
from transformers import pipeline

# Set page config
st.set_page_config(layout="wide", page_title="🧠 Hugging Face NLP App")

# Title
st.title("🧠 Hugging Face Sentiment Analysis")
st.write("Type a sentence below and let the model predict the sentiment!")

# Load the Hugging Face pipeline
@st.cache_resource
def load_model():
    return pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

classifier = load_model()

# User input
user_input = st.text_area("✍️ Enter your text here:", "Hugging Face is amazing!")

# Predict
if st.button("🔍 Analyze Sentiment"):
    if user_input.strip():
        with st.spinner("Analyzing..."):
            result = classifier(user_input)
            label = result[0]['label']
            score = result[0]['score']
            st.success(f"**Prediction**: {label} with **{score:.2%}** confidence")
    else:
        st.warning("Please enter some text.")

