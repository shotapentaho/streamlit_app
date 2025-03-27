import streamlit as st
from transformers import pipeline

#Initialize the Hugging Face sentiment analysis pipeline for multi-class sentiment (positive, negative, neutral)
sentiment_analyzer = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment")

# Streamlit UI elements
st.title("Sentiment analysis..")
st.write(
    "This is a simple application to analyze the sentiment of a text input. Enter some text and click 'Analyze' to get the sentiment result."
)

# User input text box
user_input = st.text_area("Enter text for sentiment analysis:", "")

# Button to analyze sentiment
if st.button("Analyze"):
    if user_input.strip() == "":
        st.warning("⚠ Please enter some text for analysis.")
    else:
        # Perform sentiment analysis
        result = sentiment_analyzer(user_input)
        
        # Extract sentiment result
        label = result[0]['label']
        score = result[0]['score']
        
        # Logic to detect neutral sentiment if positive and negative are close
        if label == "NEGATIVE" and score < 0.60:
            st.subheader("Sentiment: Neutral")
            st.markdown('<h3 style="color:gray;">Neutral Sentiment</h3>', unsafe_allow_html=True)
        else:
            st.subheader(f"Sentiment: {label}")
            st.write(f"Confidence Score: {score:.2f}")
            if label == "POSITIVE":
                st.markdown('<h3 style="color:green;">Positive Sentiment</h3>', unsafe_allow_html=True)
            else:
                st.markdown('<h3 style="color:red;">Negative Sentiment</h3>', unsafe_allow_html=True)