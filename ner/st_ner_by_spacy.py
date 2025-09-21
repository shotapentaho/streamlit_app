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

def build_patterns_for_label(phrases, label):
    """
    Build case-insensitive token patterns for EntityRuler from a list of phrases for a given label.
    """
    patterns = []
    for phrase in phrases:
        p = phrase.strip()
        if not p:
            continue
        tokens = p.split()
        token_pattern = [{"LOWER": w.lower()} for w in tokens]
        patterns.append({"label": label, "pattern": token_pattern})
    return patterns

def apply_overrides(nlp_obj, overrides_map):
    """
    Combine all override patterns into a single EntityRuler applied before 'ner'.
    overrides_map: dict of {label: [phrases]}
    """
    # Remove existing ruler to avoid duplicate additions on reruns
    if "entity_ruler" in nlp_obj.pipe_names:
        nlp_obj.remove_pipe("entity_ruler")
    ruler = nlp_obj.add_pipe("entity_ruler", before="ner", config={"overwrite_ents": True})

    all_patterns = []
    for label, phrases in overrides_map.items():
        all_patterns.extend(build_patterns_for_label(phrases, label))

    if all_patterns:
        ruler.add_patterns(all_patterns)

def parse_text_area_csv(value: str):
    """
    Parse a comma-separated text area into a list of trimmed, non-empty strings.
    """
    return [t.strip() for t in (value or "").split(",") if t.strip()]

def parse_uploaded_lines(upload) -> list:
    """
    Parse an uploaded .txt file (one item per line) into a list.
    """
    if upload is None:
        return []
    try:
        content = upload.read().decode("utf-8", errors="replace")
        return [line.strip() for line in content.splitlines() if line.strip()]
    except Exception:
        return []

# Sidebar: Overrides
st.sidebar.header("Overrides")

# Tools / Products -> PRODUCT
with st.sidebar.expander("Tools / Products → PRODUCT", expanded=True):
    use_tools_override = st.checkbox("Enable tools/products override", value=True, key="tools_enable")
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
        "Excel", "Word", "PowerPoint", "Pentaho", "Informatica", "Pentaho Businees Analytics",
        "Pentaho Data Integration"
    ]
    tools_text = st.text_area(
        "Known tools/products (comma-separated)",
        value=", ".join(default_tools_list),
        height=100,
        key="tools_text"
    )
    tools_upload = st.file_uploader("...or upload .txt (one per line)", type=["txt"], key="tools_upload")
    tools_list = parse_uploaded_lines(tools_upload) or parse_text_area_csv(tools_text)

# Organizations -> ORG
with st.sidebar.expander("Organizations → ORG", expanded=False):
    use_org_override = st.checkbox("Enable organizations override", value=False, key="org_enable")
    org_text = st.text_area("Organizations (comma-separated)", value="", height=80, key="org_text")
    org_upload = st.file_uploader("...or upload .txt (one per line)", type=["txt"], key="org_upload")
    org_list = parse_uploaded_lines(org_upload) or parse_text_area_csv(org_text)

# People -> PERSON
with st.sidebar.expander("People → PERSON", expanded=False):
    use_person_override = st.checkbox("Enable people override", value=False, key="person_enable")
    person_text = st.text_area("People (comma-separated)", value="", height=80, key="person_text")
    person_upload = st.file_uploader("...or upload .txt (one per line)", type=["txt"], key="person_upload")
    person_list = parse_uploaded_lines(person_upload) or parse_text_area_csv(person_text)

# Locations -> GPE (countries, cities)
with st.sidebar.expander("Locations → GPE", expanded=False):
    use_gpe_override = st.checkbox("Enable locations override", value=False, key="gpe_enable")
    gpe_text = st.text_area("Locations (comma-separated)", value="", height=80, key="gpe_text")
    gpe_upload = st.file_uploader("...or upload .txt (one per line)", type=["txt"], key="gpe_upload")
    gpe_list = parse_uploaded_lines(gpe_upload) or parse_text_area_csv(gpe_text)

# Dates -> DATE
with st.sidebar.expander("Dates → DATE", expanded=False):
    use_date_override = st.checkbox("Enable dates override", value=False, key="date_enable")
    date_text = st.text_area("Dates/Date-like phrases (comma-separated)", value="", height=80, key="date_text")
    date_upload = st.file_uploader("...or upload .txt (one per line)", type=["txt"], key="date_upload")
    date_list = parse_uploaded_lines(date_upload) or parse_text_area_csv(date_text)

# Groups (nationalities, religious, political) -> NORP
with st.sidebar.expander("Groups → NORP", expanded=False):
    use_norp_override = st.checkbox("Enable groups override", value=False, key="norp_enable")
    norp_text = st.text_area("Groups (comma-separated)", value="", height=80, key="norp_text")
    norp_upload = st.file_uploader("...or upload .txt (one per line)", type=["txt"], key="norp_upload")
    norp_list = parse_uploaded_lines(norp_upload) or parse_text_area_csv(norp_text)

# Build the active overrides map
overrides = {}
if use_tools_override and tools_list:
    overrides["PRODUCT"] = tools_list
if use_org_override and org_list:
    overrides["ORG"] = org_list
if use_person_override and person_list:
    overrides["PERSON"] = person_list
if use_gpe_override and gpe_list:
    overrides["GPE"] = gpe_list
if use_date_override and date_list:
    overrides["DATE"] = date_list
if use_norp_override and norp_list:
    overrides["NORP"] = norp_list

# File upload (content)
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
        try:
            if uploaded_file.type and uploaded_file.type.startswith("text/"):
                raw = uploaded_file.read()
                try:
                    text = raw.decode("utf-8", errors="replace")
                except Exception:
                    text = raw.decode("latin-1", errors="replace")
            else:
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

# Apply all rule-based overrides before running NER
if overrides:
    apply_overrides(nlp, overrides)
else:
    # If no overrides enabled, ensure we don't keep a stale ruler from a prior run
    if "entity_ruler" in nlp.pipe_names:
        nlp.remove_pipe("entity_ruler")

# Process text with spaCy
if text and text.strip():
    with st.spinner("Running NER..."):
        doc = nlp(text)

    # Dropdowns for ALL entity labels (ORG filters out known tools/products)
    st.subheader("📂 Entity Dropdowns by Label")
    labels = sorted({ent.label_ for ent in doc.ents})
    if labels:
        dd_cols = st.columns(min(4, max(1, len(labels))))
        dd_cycle = dd_cols * ((len(labels) // max(1, len(dd_cols))) + 1)

        tool_norm = {t.casefold().strip() for t in (tools_list or [])}

        for label, col in zip(labels, dd_cycle):
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

    # Keep colored displaCy visualization
    st.subheader("🖼 Entity Visualization")
    max_chars_for_viz = st.slider("Max characters for visualization", 500, 10000, 4000, step=500)
    viz_text = text[:max_chars_for_viz]
    viz_doc = nlp(viz_text)
    html = displacy.render(viz_doc, style="ent", jupyter=False)
    st.markdown(html, unsafe_allow_html=True)

    if len(text) > max_chars_for_viz:
        st.caption("Visualization truncated to the selected character limit to keep the app responsive.")
else:
    st.info("Provide text (or upload a .txt/.pdf) to analyze.")