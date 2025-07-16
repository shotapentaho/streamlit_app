import streamlit as st
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import re
import pandas as pd

st.set_page_config(layout="wide") 

# Available models
available_models = {
    "DistilBERT (SST-2, English)": "distilbert-base-uncased-finetuned-sst-2-english",
    "Twitter RoBERTa (English)": "cardiffnlp/twitter-roberta-base-sentiment",
    "Multilingual BERT (NLPTown)": "nlptown/bert-base-multilingual-uncased-sentiment"
}

st.title("Sentiment Analysis - Compare Models (Table)")

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
        results = []
        for model_label, analyzer in analyzers.items():
            try:
                result = analyzer(user_input)[0]
            except Exception as e:
                results.append({
                    "Model": model_label,
                    "Sentiment": "ERROR",
                    "Confidence": "-",
                    "Stars": "-",
                    "Color": "gray"
                })
                continue

            label = result['label']
            score = result['score']
            stars = "-"
            sentiment_display = label

            if "star" in label:
                match = re.search(r"(\d)", label)
                if match:
                    num_stars = int(match.group(1))
                else:
                    num_stars = 3
                stars = rating_to_stars(num_stars)
                sentiment_display = stars

            if label.lower().startswith("pos"):
                color = "green"
                sentiment_label = "Positive"
            elif label.lower().startswith("neg"):
                color = "red"
                sentiment_label = "Negative"
            else:
                color = "gray"
                sentiment_label = "Neutral" if "star" not in label else f"{label}"

            results.append({
                "Model": model_label,
                "Sentiment": sentiment_label,
                "Confidence": f"{score:.2f}",
                "Stars": stars if stars != "-" else "",
                "Color": color
            })

        df = pd.DataFrame(results)
        # Show sentiment with colored markdown
        def color_row(row):
            return [f'background-color: {row.Color}; color: white' if c == 'Sentiment' else '' for c in df.columns]

        st.dataframe(df[["Model", "Sentiment", "Confidence", "Stars"]], use_container_width=True)