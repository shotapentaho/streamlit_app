import streamlit as st
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import re

# Available models
available_models = {
    "DistilBERT (SST-2, English)": "distilbert-base-uncased-finetuned-sst-2-english",
    "Twitter RoBERTa (English)": "cardiffnlp/twitter-roberta-base-sentiment",
    "Multilingual BERT (NLPTown)": "nlptown/bert-base-multilingual-uncased-sentiment"
}

st.title("Sentiment Analysis - Compare Models")

# Load all models and cache them
@st.cache_resource
def load_model(model_name):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    return pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

# Function to convert a numeric rating into stars
def rating_to_stars(rating):
    full_star = "⭐"
    empty_star = "☆"
    full_stars = full_star * rating
    empty_stars = empty_star * (5 - rating)
    return full_stars + empty_stars

# Load all analyzers at once
analyzers = {name: load_model(model) for name, model in available_models.items()}

user_input = st.text_area("Enter some text:", "")

if st.button("Analyze"):
    if not user_input.strip():
        st.warning("⚠ Please enter some text for analysis.")
    else:
        cols = st.columns(len(analyzers))
        for i, (model_label, analyzer) in enumerate(analyzers.items()):
            with cols[i]:
                st.markdown(f"### {model_label}")
                try:
                    result = analyzer(user_input)[0]
                except Exception as e:
                    st.error(f"Error: {e}")
                    continue
                label = result['label']
                score = result['score']
                if "star" in label:
                    match = re.search(r"(\d)", label)
                    if match:
                        num_stars = int(match.group(1))
                    else:
                        num_stars = 3
                    star_display = rating_to_stars(num_stars)
                    st.subheader(f"Sentiment: {star_display}") 
                else:
                    st.subheader(f"Sentiment: {label}")
                st.write(f"Confidence Score: {score:.2f}")
                if label.lower().startswith("pos"):
                    st.markdown('<h3 style="color:green;">Positive</h3>', unsafe_allow_html=True)
                elif label.lower().startswith("neg"):
                    st.markdown('<h3 style="color:red;">Negative</h3>', unsafe_allow_html=True)
                else:
                    st.markdown('<h3 style="color:gray;">Neutral</h3>', unsafe_allow_html=True)