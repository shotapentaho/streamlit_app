import streamlit as st
from transformers import pipeline

# Set page config
st.set_page_config(page_title="Hate Speech Detector", page_icon="🛑", layout="centered")

# Available models
MODEL_OPTIONS = {
    "Roberta Dynabench (facebook/roberta-hate-speech-dynabench-r4-target)": "facebook/roberta-hate-speech-dynabench-r4-target",
    "Toxic BERT (unitary/toxic-bert)": "unitary/toxic-bert",
    "Hatexplain BERT (Hate-speech-CNERG/bert-base-uncased-hatexplain)": "Hate-speech-CNERG/bert-base-uncased-hatexplain",
}

# Load the selected model
@st.cache_resource
def load_model(model_name):
    return pipeline("text-classification", model=model_name)

# UI layout
st.title("🛑 Hate Speech Detection (HuggingFace + Streamlit)")
st.markdown("Select a model, enter text, and detect hate speech using powerful transformers.")

# Dropdown for model selection
model_label = st.selectbox("Choose a model", list(MODEL_OPTIONS.keys()))
model_name = MODEL_OPTIONS[model_label]

# Load and cache the selected model
classifier = load_model(model_name)

# Text input
text_input = st.text_area("Text to Analyze", height=200)

# Analysis
if st.button("Analyze"):
    if not text_input.strip():
        st.warning("Please enter some text.")
    else:
        with st.spinner("Analyzing..."):
            results = classifier(text_input)
        st.subheader("🧠 Model Output")
        for result in results:
            st.markdown(f"- **Label**: `{result['label']}` | **Confidence**: `{result['score'] * 100:.2f}%`")
