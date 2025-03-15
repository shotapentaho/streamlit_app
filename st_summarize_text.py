import streamlit as st
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

# Function to summarize text
def summarize_text(text, num_sentences):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, num_sentences)
    return " ".join(str(sentence) for sentence in summary)

# Streamlit UI
st.title("Text Summarizer")

# Text input
text = st.text_area("Enter text to summarize:", height=200)

# Select number of sentences
num_sentences = st.slider("Number of summary sentences:", 1, 10, 3)

# Summarize button
if st.button("Summarize"):
    if text.strip():
        summary = summarize_text(text, num_sentences)
        st.subheader("Summary:")
        st.write(summary)
    else:
        st.warning("Please enter some text to summarize.")
