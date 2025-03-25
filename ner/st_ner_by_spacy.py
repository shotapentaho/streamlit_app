import streamlit as st
import spacy
from spacy import displacy
from spacy.cli import download

# Check if model is available, if not, install it
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    #st.error("Error: en_core_web_sm model not found. Please install it using `python -m spacy download en_core_web_sm`.")
    #st.stop()
    print("Downloading en_core_web_sm...")
    download("en_core_web_sm")
    #nlp = spacy.load("en_core_web_sm")

# Load spaCy Model
nlp = spacy.load("en_core_web_sm")
print("Model loaded successfully!")

# Streamlit UI
st.title("📝 Named Entity Recognition (NER) App")

# Input text or file upload
uploaded_file = st.file_uploader("Upload a text file", type=["txt"])

if uploaded_file:
    text = uploaded_file.read().decode("utf-8")
else:
    text = st.text_area("Enter text here:", "Apple Inc. was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne in Cupertino, California, in 1976.")

# Process text with spaCy
if text:
    doc = nlp(text)
    
    # Display Named Entities
    st.subheader("🔍 Detected Entities")
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    
    if entities:
        for entity, label in entities:
            st.write(f"**{entity}** - `{label}`")
    else:
        st.write("No named entities detected.")

    # Render with spaCy's visualization
    st.subheader("🖼 Entity Visualization")
    html = displacy.render(doc, style="ent", jupyter=False)
    st.markdown(html, unsafe_allow_html=True)
