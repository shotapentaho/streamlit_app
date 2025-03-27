import streamlit as st
from transformers import pipeline

# Initialize the Hugging Face sentiment analysis pipeline
sentiment_analyzer = pipeline("sentiment-analysis")

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
        
        # Display results
        st.subheader(f"Sentiment: {label}")
        st.write(f"Confidence Score: {score:.2f}")

        # Show the result's sentiment color
        if label == 'POSITIVE':
            st.markdown('<h3 style="color:green;">Positive Sentiment</h3>', unsafe_allow_html=True)
        else:
            st.markdown('<h3 style="color:red;">Negative Sentiment</h3>', unsafe_allow_html=True)

