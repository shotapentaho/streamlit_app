import streamlit as st
from openai import OpenAI
from PyPDF2 import PdfReader
import json
import re
import html
from typing import List, Dict, Any, Tuple

# -------------------------
# App config
# -------------------------
st.set_page_config(page_title="LLM NER for PDF/TXT", layout="wide")
st.title("🧠 LLM-powered NER for PDF/TXT")
st.caption("Upload a PDF or TXT, extract named entities with OpenAI, browse by label, and view color-coded highlights.")

# -------------------------
# Secrets and client
# -------------------------
# Expecting st.secrets["openai"]["api_key"]
try:
    client = OpenAI(api_key=st.secrets["openai"]["api_key"])
except Exception:
    client = None
    st.error("OpenAI API key is missing. Add it to Streamlit secrets as:\n[openai]\napi_key = 'sk-...'")


# -------------------------
# Utility: PDF text extraction
# -------------------------
def extract_text_from_pdf(file) -> str:
    try:
        reader = PdfReader(file)
        texts = []
        for page in reader.pages:
            try:
                t = page.extract_text() or ""
            except Exception:
                t = ""
            if t:
                texts.append(t)
        return "\n\n".join(texts).strip()
    except Exception as e:
        st.error(f"Failed to read PDF: {e}")
        return ""


# -------------------------
# Chunking
# -------------------------
def chunk_text(text: str, chunk_size: int = 3000, overlap: int = 200) -> List[Tuple[int, str]]:
    """
    Split text into overlapping character chunks.
    Returns a list of (offset_in_original, chunk_text).
    """
    chunks: List[Tuple[int, str]] = []
    n = len(text)
    start = 0
    while start < n:
        end = min(start + chunk_size, n)
        segment = text[start:end]
        if segment:
            chunks.append((start, segment))
        # ensure forward progress even if overlap >= chunk_size
        start += max(1, chunk_size - overlap)
    return chunks


# -------------------------
# LLM NER call
# -------------------------
DEFAULT_LABELS = [
    "PERSON", "ORG", "GPE", "LOC", "PRODUCT", "EVENT", "WORK_OF_ART",
    "LAW", "LANGUAGE", "DATE", "TIME", "PERCENT", "MONEY", "QUANTITY",
    "ORDINAL", "CARDINAL", "NORP", "FAC"
]

def parse_json_from_text(s: str) -> Dict[str, Any]:
    """
    Robustly parse JSON from a model response.
    Tries to find a JSON block in triple backticks; falls back to the first {...} object.
    """
    # Try code block
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", s, flags=re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    # Try first JSON object
    first_brace = s.find("{")
    last_brace = s.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        try:
            return json.loads(s[first_brace:last_brace+1])
        except Exception:
            pass
    # Fallback
    return {"entities": []}

def call_openai_ner(text: str, model: str = "gpt-4o-mini", labels: List[str] = DEFAULT_LABELS, max_tokens: int = 800) -> List[Dict[str, Any]]:
    """
    Calls OpenAI chat to perform NER on the given text.
    Returns a list of entities with fields: text, label, start, end.
    """
    if not client:
        return []

    system_prompt = (
        "You are a precise NER engine. Extract named entities from the user's text.\n"
        "- Only use the allowed labels provided.\n"
        "- Return absolute character offsets relative to the input text you are given.\n"
        "- Avoid overlapping entities; if boundaries collide, prefer the longer, more specific span.\n"
        "- If uncertain, omit the entity.\n"
        "- Respond with pure JSON only, in this exact schema:\n"
        "{\n"
        '  "entities": [\n'
        '    {"text": "...", "label": "ORG", "start": 10, "end": 22}\n'
        "  ]\n"
        "}\n"
    )
    user_prompt = (
        f"Allowed labels: {labels}\n\n"
        "Text:\n"
        f"{text}"
    )

    resp = client.chat.completions.create(
        model=model,
        temperature=0.0,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    content = resp.choices[0].message.content or ""
    data = parse_json_from_text(content)
    entities = data.get("entities", [])
    # Basic validation/coercion
    cleaned = []
    for e in entities:
        try:
            t = str(e["text"])
            lab = str(e["label"]).upper().strip()
            s = int(e["start"])
            en = int(e["end"])
            if s >= 0 and en >= s and lab in labels:
                cleaned.append({"text": t, "label": lab, "start": s, "end": en})
        except Exception:
            continue
    return cleaned


# -------------------------
# Entity merging, overlap resolution
# -------------------------
def adjust_entities_for_offset(ents: List[Dict[str, Any]], offset: int) -> List[Dict[str, Any]]:
    out = []
    for e in ents:
        out.append({
            "text": e["text"],
            "label": e["label"],
            "start": e["start"] + offset,
            "end": e["end"] + offset
        })
    return out

def dedup_and_resolve_overlaps(entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    - Remove exact duplicates.
    - Resolve overlaps by keeping the longer span when two entities overlap.
    """
    # Remove exact duplicates
    unique = {(e["start"], e["end"], e["label"], e["text"]): e for e in entities}
    entities = list(unique.values())

    # Sort by start, then by longer span first
    entities.sort(key=lambda e: (e["start"], -(e["end"] - e["start"])))

    resolved: List[Dict[str, Any]] = []
    for e in entities:
        if not resolved:
            resolved.append(e)
            continue
        last = resolved[-1]
        # If no overlap, accept
        if e["start"] >= last["end"]:
            resolved.append(e)
        else:
            # Overlap: keep the longer span
            curr_len = e["end"] - e["start"]
            last_len = last["end"] - last["start"]
            if curr_len > last_len:
                resolved[-1] = e  # replace with longer
            # else keep last and drop e
    return resolved


# -------------------------
# Rendering: colored HTML
# -------------------------
PALETTE = {
    "PERSON": "#fde68a",
    "ORG": "#bfdbfe",
    "GPE": "#c7f9cc",
    "LOC": "#fbcfe8",
    "PRODUCT": "#d1fae5",
    "EVENT": "#fecaca",
    "WORK_OF_ART": "#f5d0fe",
    "LAW": "#e9d5ff",
    "LANGUAGE": "#e5e7eb",
    "DATE": "#fef3c7",
    "TIME": "#e0e7ff",
    "PERCENT": "#fce7f3",
    "MONEY": "#dcfce7",
    "QUANTITY": "#ffedd5",
    "ORDINAL": "#f3e8ff",
    "CARDINAL": "#e2e8f0",
    "NORP": "#fde2e4",
    "FAC": "#fee2e2",
}

def label_color(label: str) -> str:
    return PALETTE.get(label.upper(), "#e5e7eb")

def render_colored(text: str, entities: List[Dict[str, Any]]) -> str:
    """
    Render text with <span> highlights per entity.
    """
    safe = []
    cursor = 0
    for e in entities:
        s, en, lab = e["start"], e["end"], e["label"]
        # Safety bounds
        s = max(0, min(s, len(text)))
        en = max(0, min(en, len(text)))
        if en <= s:
            continue
        if s > cursor:
            safe.append(html.escape(text[cursor:s]))
        color = label_color(lab)
        tip = f"{lab}"
        ent_html = f'<span style="background:{color}; padding:1px 3px; border-radius:4px;" title="{html.escape(tip)}">{html.escape(text[s:en])}</span>'
        safe.append(ent_html)
        cursor = en
    if cursor < len(text):
        safe.append(html.escape(text[cursor:]))
    return "".join(safe)

def group_by_label(entities: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    by = {}
    for e in entities:
        by.setdefault(e["label"], []).append(e)
    return by


# -------------------------
# Sidebar controls
# -------------------------
st.sidebar.header("Settings")
model = st.sidebar.selectbox(
    "OpenAI model",
    options=["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
    index=0
)
chunk_size = st.sidebar.slider("Chunk size (chars)", 1000, 8000, 3000, 250)
overlap = st.sidebar.slider("Chunk overlap (chars)", 0, 1000, 200, 50)
max_tokens = st.sidebar.slider("Max tokens per chunk (LLM output)", 200, 2000, 800, 50)
preview_limit = st.sidebar.slider("Max characters to visualize", 500, 30000, 8000, 500)
labels_selected = st.sidebar.multiselect(
    "Entity labels to extract",
    options=DEFAULT_LABELS,
    default=DEFAULT_LABELS
)

st.sidebar.caption("Tip: Increase chunk size for long paragraphs; keep overlap ~5–15% of chunk size.")


# -------------------------
# Input area
# -------------------------
uploaded = st.file_uploader("Upload a PDF or TXT", type=["pdf", "txt"])
text_input = st.text_area("Or paste text here (will be used if no file is uploaded):", height=150)

source_text = ""
file_info = ""

if uploaded is not None:
    if uploaded.type == "application/pdf":
        with st.spinner("Extracting text from PDF..."):
            source_text = extract_text_from_pdf(uploaded)
        file_info = f"Loaded from PDF: {uploaded.name}"
        if not source_text:
            st.warning("No extractable text found (scanned/image-only PDF). Consider OCR.")
    else:
        try:
            source_text = uploaded.read().decode("utf-8", errors="replace")
            file_info = f"Loaded from text file: {uploaded.name}"
        except Exception as e:
            st.error(f"Failed to read text file: {e}")
            source_text = ""

if not source_text and text_input.strip():
    source_text = text_input.strip()
    file_info = "Text entered in the input box."

if file_info:
    st.caption(file_info)


# -------------------------
# Run NER
# -------------------------
if source_text:
    if not client:
        st.stop()

    chunks = chunk_text(source_text, chunk_size=chunk_size, overlap=overlap)
    st.write(f"Document split into {len(chunks)} chunks.")

    all_entities: List[Dict[str, Any]] = []

    with st.spinner("Running NER with OpenAI..."):
        for off, seg in chunks:
            ents = call_openai_ner(seg[:8000], model=model, labels=labels_selected, max_tokens=max_tokens)
            if not ents:
                continue
            all_entities.extend(adjust_entities_for_offset(ents, off))

    if not all_entities:
        st.info("No entities detected.")
        st.stop()

    # Resolve overlaps and sort
    entities_resolved = dedup_and_resolve_overlaps(all_entities)
    entities_resolved.sort(key=lambda e: (e["start"], e["end"]))

    # Dropdowns per label
    st.subheader("📂 Entity Dropdowns by Label")
    by_label = group_by_label(entities_resolved)
    labels_present = sorted(by_label.keys())
    if labels_present:
        cols = st.columns(min(4, len(labels_present)))
        col_cycle = cols * ((len(labels_present) // max(1, len(cols))) + 1)
        for lab, col in zip(labels_present, col_cycle):
            with col:
                options = sorted({e["text"] for e in by_label[lab]}, key=str.casefold)
                st.markdown(f"**{lab}** ({len(by_label[lab])})")
                if options:
                    sel = st.selectbox(f"Select {lab}", options=options, key=f"dd_{lab}")
                    occ = sum(1 for e in by_label[lab] if e["text"] == sel)
                    st.caption(f"Occurrences: {occ}")
                else:
                    st.caption("No entities for this label.")
    else:
        st.write("No entities detected.")

    # Color-coded visualization
    st.subheader("🖼 Color-coded Entity Visualization")
    viz_text = source_text[:preview_limit]
    # Filter entities to those within viz range
    viz_ents = [e for e in entities_resolved if e["start"] < len(viz_text) and e["end"] > 0]
    # Clamp spans
    for e in viz_ents:
        e["start"] = max(0, min(e["start"], len(viz_text)))
        e["end"] = max(0, min(e["end"], len(viz_text)))
    html_viz = render_colored(viz_text, viz_ents)
    legend = " ".join(
        f'<span style="background:{label_color(l)};padding:2px 6px;border-radius:4px;margin-right:6px;">{html.escape(l)}</span>'
        for l in labels_present
    )
    st.markdown(f'<div style="margin-bottom:8px;">{legend}</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="white-space:pre-wrap; line-height:1.6;">{html_viz}</div>', unsafe_allow_html=True)

    if len(source_text) > preview_limit:
        st.caption("Visualization truncated to the selected character limit. Increase the limit in the sidebar to view more.")
else:
    st.info("Upload a PDF/TXT or paste text to begin.")