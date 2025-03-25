import streamlit as st
import spacy
from spacy import displacy

spacy.download("en_core_web_sm")

# Load spaCy Model
nlp = spacy.load("en_core_web_sm")

# Streamlit UI
st.title("📝 Named Entity Recognition (NER) App")

# Input text or file upload
uploaded_file = st.file_uploader("Upload a text file", type=["txt"])

if uploaded_file:
    text = uploaded_file.read().decode("utf-8")
else:
    text = st.text_area("Enter text here:", "Barack Obama was the 44th President of the United States.")

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
