import streamlit as st
import spacy
from spacy import displacy
from spacy.cli import download

# PDF support
try:
    from pypdf import PdfReader  # lightweight, pure-Python
    HAS_PYPDF = True
except Exception:
    HAS_PYPDF = False

st.set_page_config(page_title="Named Entity Recognition (NER)", layout="wide")
st.title("📝 Named Entity Recognition (NER)")
st.caption("Upload a .txt or .pdf file, or type/paste text below, then view detected entities and a visualization.")

# Ensure spaCy model is available
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    with st.spinner("Downloading spaCy model en_core_web_sm..."):
        download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

def extract_text_from_pdf(uploaded_file) -> str:
    """
    Extract text from a PDF using pypdf. Returns best-effort text string.
    """
    if not HAS_PYPDF:
        st.error("PDF support requires the 'pypdf' package. Install with: pip install pypdf")
        return ""

    try:
        reader = PdfReader(uploaded_file)
        texts = []
        for page in reader.pages:
            try:
                txt = page.extract_text() or ""
            except Exception:
                txt = ""
            if txt:
                texts.append(txt)
        return "\n\n".join(texts).strip()
    except Exception as e:
        st.error(f"Failed to read PDF: {e}")
        return ""

def is_pdf_file(file) -> bool:
    """
    Detect PDFs robustly using MIME type or filename extension.
    """
    mime = (file.type or "").lower()
    name = (file.name or "").lower()
    return ("application/pdf" in mime) or name.endswith(".pdf")

# Remove 'type' filter to avoid browser-level filtering issues; detect ourselves
uploaded_file = st.file_uploader("Upload a file (.txt or .pdf)", accept_multiple_files=False)

default_text = (
    "Apple Inc. was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne "
    "in Cupertino, California, in 1976."
)

text = ""
file_info = ""

if uploaded_file is not None:
    filename = uploaded_file.name or "uploaded_file"
    if is_pdf_file(uploaded_file):
        with st.spinner("Extracting text from PDF..."):
            text = extract_text_from_pdf(uploaded_file)
        file_info = f"Loaded from PDF: {filename}"
        if not text:
            st.warning("No extractable text found in the PDF (it may be scanned images). Try a text-based PDF or paste text below.")
    else:
        # Treat as text if MIME indicates text/* or extension looks like .txt
        try:
            if uploaded_file.type and uploaded_file.type.startswith("text/"):
                raw = uploaded_file.read()
                # Try utf-8 then fallback to latin-1
                try:
                    text = raw.decode("utf-8", errors="replace")
                except Exception:
                    text = raw.decode("latin-1", errors="replace")
            else:
                # Fallback by extension
                if filename.lower().endswith((".txt", ".md", ".rtf")):
                    raw = uploaded_file.read()
                    try:
                        text = raw.decode("utf-8", errors="replace")
                    except Exception:
                        text = raw.decode("latin-1", errors="replace")
                else:
                    st.error("Unrecognized file type. Please upload a .txt or .pdf file.")
                    text = ""
            file_info = f"Loaded from text file: {filename}"
        except Exception as e:
            st.error(f"Failed to read file: {e}")
            text = ""
else:
    text = st.text_area("Enter text here:", default_text, height=150)

if file_info:
    st.caption(file_info)

# Process text with spaCy
if text and text.strip():
    with st.spinner("Running NER..."):
        doc = nlp(text)

    st.subheader("🔍 Detected Entities")
    entities = [(ent.text, ent.label_) for ent in doc.ents]

    if entities:
        # Group by label for easier scanning
        from collections import defaultdict
        by_label = defaultdict(list)
        for ent_text, ent_label in entities:
            by_label[ent_label].append(ent_text)

        st.write(f"Found {len(entities)} entities across {len(by_label)} labels.")
        cols = st.columns(min(4, max(1, len(by_label))))
        # Cycle columns if there are more labels than columns
        col_cycle = cols * ((len(by_label) // max(1, len(cols))) + 1)
        for (label, items), col in zip(sorted(by_label.items(), key=lambda x: x[0]), col_cycle):
            with col:
                st.markdown(f"**{label}** ({len(items)})")
                for it in items[:25]:
                    st.markdown(f"- {it}")
                if len(items) > 25:
                    st.caption(f"... and {len(items) - 25} more")
    else:
        st.write("No named entities detected.")

    st.subheader("🖼 Entity Visualization")
    # Displacy can get heavy on very long texts; allow truncation for rendering
    max_chars_for_viz = st.slider("Max characters for visualization", 500, 10000, 4000, step=500)
    viz_text = text[:max_chars_for_viz]
    viz_doc = nlp(viz_text)
    html = displacy.render(viz_doc, style="ent", jupyter=False)
    st.markdown(html, unsafe_allow_html=True)

    if len(text) > max_chars_for_viz:
        st.caption("Visualization truncated to the selected character limit to keep the app responsive.")
else:
    st.info("Provide text (or upload a .txt/.pdf) to analyze.")