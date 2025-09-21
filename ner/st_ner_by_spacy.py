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

def build_tool_patterns(tools):
    """
    Build case-insensitive token patterns for EntityRuler from a list of tool names.
    """
    patterns = []
    for tool in tools:
        t = tool.strip()
        if not t:
            continue
        tokens = t.split()
        token_pattern = [{"LOWER": w.lower()} for w in tokens]
        patterns.append({"label": "PRODUCT", "pattern": token_pattern})
    return patterns

def apply_tool_overrides(nlp_obj, tools):
    """
    Add an EntityRuler before the NER component that maps known tools/products to PRODUCT.
    Overwrites conflicting labels (e.g., ORG) for those terms.
    """
    # Remove existing ruler to avoid duplicate additions on reruns
    if "entity_ruler" in nlp_obj.pipe_names:
        nlp_obj.remove_pipe("entity_ruler")
    ruler = nlp_obj.add_pipe("entity_ruler", before="ner", config={"overwrite_ents": True})
    patterns = build_tool_patterns(tools)
    if patterns:
        ruler.add_patterns(patterns)

# Sidebar controls for tool overrides
st.sidebar.header("NER Settings")
use_tool_overrides = st.sidebar.checkbox("Override known tools/products to PRODUCT (reduce ORG mislabels)", value=True)

default_tools_list = [
    "Git", "GitHub", "GitLab", "Bitbucket",
    "Docker", "Kubernetes", "Helm", "Terraform", "Ansible",
    "Jenkins", "CircleCI", "GitHub Actions", "Azure DevOps",
    "Jira", "Confluence", "Slack", "Microsoft Teams",
    "Figma", "Miro", "Notion",
    "Postman", "Insomnia", "cURL",
    "Visual Studio", "VS Code", "PyCharm", "IntelliJ",
    "Apache Spark", "Apache Kafka", "Airflow",
    "BigQuery", "Redshift", "Snowflake", "Databricks",
    "MySQL", "PostgreSQL", "MongoDB",
    "Excel", "Word", "PowerPoint",
    "Pentaho", "Informatica", "Pentaho Business Analytics", "Pentaho Businees Analytics",
    "Pentaho Data Integration"
]
tools_input = st.sidebar.text_area(
    "Known tools/products (comma-separated)",
    value=", ".join(default_tools_list),
    height=100,
)
tools_upload = st.sidebar.file_uploader("Or upload a .txt (one tool/product per line)", type=["txt"], key="tools_upload")

# Build final tool list
tools_list = []
if tools_upload is not None:
    try:
        content = tools_upload.read().decode("utf-8", errors="replace")
        tools_list = [line.strip() for line in content.splitlines() if line.strip()]
    except Exception:
        st.sidebar.warning("Failed to read uploaded file. Falling back to text area input.")
if not tools_list:
    tools_list = [t.strip() for t in tools_input.split(",") if t.strip()]

# Remove 'type' filter to avoid browser-level filtering issues; detect ourselves
uploaded_file = st.file_uploader("Upload a file (.txt or .pdf)", accept_multiple_files=False)

default_text = (
    "Apple Inc. was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne "
    "in Cupertino, California, in 1976. Apple uses tools like Git, Docker, and Jira."
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

# Apply rule-based overrides before running NER
if use_tool_overrides and tools_list:
    apply_tool_overrides(nlp, tools_list)

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

        # Dropdowns for ALL entity labels (with ORG-specific filtering of known tools)
        st.subheader("📂 Entity Dropdowns by Label")
        label_list = sorted(by_label.keys())
        dd_cols = st.columns(min(4, max(1, len(label_list))))
        dd_cycle = dd_cols * ((len(label_list) // max(1, len(dd_cols))) + 1)

        tool_norm = {t.casefold().strip() for t in tools_list}

        for label, col in zip(label_list, dd_cycle):
            with col:
                if label == "ORG":
                    options = sorted({
                        ent.text for ent in doc.ents
                        if ent.label_ == label and ent.text.casefold().strip() not in tool_norm
                    }, key=str.casefold)
                else:
                    options = sorted({ent.text for ent in doc.ents if ent.label_ == label}, key=str.casefold)

                st.markdown(f"**{label}**")
                if options:
                    selected = st.selectbox(
                        f"Select {label}",
                        options=options,
                        key=f"select_{label}"
                    )
                    occurrences = sum(1 for ent in doc.ents if ent.label_ == label and ent.text == selected)
                    st.caption(f"Occurrences in text: {occurrences}")
                else:
                    st.caption("No entities for this label.")

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