import streamlit as st
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

# Available models in the select box
available_models = {
    "DistilBERT (SST-2, English)": "distilbert-base-uncased-finetuned-sst-2-english",
    "Twitter RoBERTa (English)": "cardiffnlp/twitter-roberta-base-sentiment",
    "Multilingual BERT (NLPTown)": "nlptown/bert-base-multilingual-uncased-sentiment"
}

# Streamlit UI
st.title("Sentiment Analysis - by Models")

# Selectbox for model selection
selected_model_name = st.selectbox("Select a sentiment analysis model:", list(available_models.keys()))
model_name = available_models[selected_model_name]

st.write(f"Using model: `{model_name}`")

# Load tokenizer and model
@st.cache_resource
def load_model(model_name):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    return pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

# Function to convert a numeric rating into stars
def rating_to_stars(rating):
    # Create a full star unicode for the rating
    full_star = "⭐"
    empty_star = "☆"
    
    # Calculate how many full stars to show
    full_stars = full_star * rating
    empty_stars = empty_star * (5 - rating)
    
    return full_stars + empty_stars

sentiment_analyzer = load_model(model_name)

# Text input area
user_input = st.text_area("Enter text for sentiment analysis:", "")

# Analyze button
if st.button("Analyze"):
    if not user_input.strip():
        st.warning("⚠ Please enter some text for analysis.")
    else:
        result = sentiment_analyzer(user_input)[0]
        
        label = result['label']
        score = result['score']
        st.subheader(f"Label: {label}") 
        st.subheader(f"Score: {score}") 

        # Optional: handle neutral logic only for binary classifiers
        if "star" in label:
            star_display = rating_to_stars(3)   
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
