"""
Ask PDF! 🚀  (v13) - Main app (provider helpers moved to provider_embed_text.py; admin tools in pages/admin.py)

This file:
- Renders the main UI (upload, chunk, embed, retrieve, answer)
- Uses provider_embed_text.py for provider-specific embedding calls
- Delegates embedding/index building and retrieval/QA UI to rag_pipeline.py
- Admin probe/credentials UI lives in pages/admin.py (Streamlit Pages)
- Reads a session_state debug flag (set by Admin) and passes it to the RAG pipeline
"""
import time
import math
import json
from typing import List, Dict, Any, Tuple, Optional

import streamlit as st
import openai
import faiss
import numpy as np
from pypdf import PdfReader
import requests
from st_ui_theme import apply_theme
import tiktoken

# Provider helpers (extracted)
from provider_embed_text import (
    gemini_embed_texts as gemini_embed_helper,
    vertex_embed_texts_ui as vertex_embed_helper,
    hf_embed_texts as hf_embed_helper,
)

# Detection & OpenAI helper functions
from detect_embedding_model import (
    detect_available_gemini_embedding_models,
    detect_openai_embedding_models,
    detect_vertex_embedding_models,
    openai_embed_texts,
    GEMINI_API_BASES,
    KNOWN_GEMINI_EMBEDDING_CANDIDATES,
    KNOWN_VERTEX_EMBEDDING_CANDIDATES,
)

# RAG pipeline helpers (indexing + retrieval UI)
from rag_pipeline import build_embeddings_and_index, run_retrieval_ui

# ---------------- small helper: safe rerun ----------------
def safe_rerun():
    try:
        rerun = getattr(st, "experimental_rerun", None)
        if callable(rerun):
            rerun()
            return
    except Exception:
        pass
    try:
        st.experimental_set_query_params(_rerun=str(time.time()))
        return
    except Exception:
        pass
    try:
        st.stop()
    except Exception:
        raise SystemExit()

# ---------------- UI & Theme ----------------
st.set_page_config(page_title="Ask PDF! 🚀 RAG with FAISS", layout="wide")
apply_theme()
st.markdown("<style>#MainMenu {visibility: hidden;}</style>", unsafe_allow_html=True)

# ---------------- Secrets / Keys / GCP ----------------
openai_api_key = st.secrets.get("openai", {}).get("api_key")
gemini_api_key = st.secrets.get("gemini", {}).get("api_key")
huggingface_api_token = st.secrets.get("huggingface", {}).get("api_token")

# Vertex service account + project/location (optional)
gcp_sa_json = None
gcp_project = None
gcp_location = None
if "gcp" in st.secrets:
    gcp = st.secrets["gcp"]
    gcp_sa_json = gcp.get("service_account")
    gcp_project = gcp.get("project")
    gcp_location = gcp.get("location")

gcp_sa_info = None
if gcp_sa_json:
    if isinstance(gcp_sa_json, str):
        try:
            gcp_sa_info = json.loads(gcp_sa_json)
        except Exception:
            gcp_sa_info = None
    elif isinstance(gcp_sa_json, dict):
        gcp_sa_info = gcp_sa_json

# ---------------- Detect available embedding models ----------------
detected_gemini_embeds: List[str] = []
try:
    detected_gemini_embeds = detect_available_gemini_embedding_models(gemini_api_key) or []
except Exception:
    detected_gemini_embeds = []

detected_openai_embeds: List[str] = []
try:
    detected_openai_embeds = detect_openai_embedding_models(openai_api_key) or []
except Exception:
    detected_openai_embeds = []

detected_vertex_embeds: List[str] = []
if gcp_sa_info and gcp_project and gcp_location:
    try:
        detected_vertex_embeds = detect_vertex_embedding_models(gcp_sa_info, gcp_project, gcp_location) or []
    except Exception:
        detected_vertex_embeds = []

ss = st.session_state
ss.setdefault("detected_gemini_embeds", detected_gemini_embeds)
ss.setdefault("detected_openai_embeds", detected_openai_embeds)
ss.setdefault("detected_vertex_embeds", detected_vertex_embeds)

# ---------------- Model registries ----------------
HF_MODELS = {
    "BAAI/bge-large-en-v1.5": "BAAI/bge-large-en-v1.5",
    "BAAI/bge-small-en-v1.5": "BAAI/bge-small-en-v1.5",
}
OPENAI_DEFAULTS = {
    "text-embedding-ada-002": "text-embedding-ada-002",
    "text-embedding-3-large": "text-embedding-3-large",
    "text-embedding-3-small": "text-embedding-3-small"
}
if ss.get("detected_openai_embeds"):
    openai_map = {m: m for m in ss["detected_openai_embeds"]}
elif detected_openai_embeds:
    openai_map = {m: m for m in detected_openai_embeds}
else:
    openai_map = OPENAI_DEFAULTS

gemini_list = ss.get("detected_gemini_embeds") or detected_gemini_embeds or []
gemini_map = {m: m for m in gemini_list} if gemini_list else {}
vertex_list = ss.get("detected_vertex_embeds") or detected_vertex_embeds or []
vertex_map = {m: m for m in vertex_list} if vertex_list else {}

EMBED_MODELS = {
    "OpenAI": openai_map,
    "Gemini": gemini_map,
    "Vertex": vertex_map,
    "HuggingFace": HF_MODELS,
}

# ---------------- Sidebar: pointer to Admin page ----------------
#with st.sidebar:
#    st.markdown("### App")
#    st.info("Admin probe/debug tools moved to the separate 'Admin' page (Pages → Admin).")

# ---------------- UI variables / defaults ----------------
OPENAI_CHAT_MODELS = ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"]
GEMINI_CHAT_CANDIDATES = [
    "gemini-3-pro-preview",
    "gemini-2.5-pro",
    "gemini-2.0-flash",
    "gemini-1.5-flash-8b",
    "gemini-2.5-flash",
    "gemini-2.5-lite",
]
GEMINI_API_BASE = GEMINI_API_BASES[0]

# ---------------- Session State defaults ----------------
ss.setdefault("chunks", [])
ss.setdefault("model_embeddings", {})
ss.setdefault("model_indexes", {})
ss.setdefault("pdf_loaded", False)
ss.setdefault("last_file_name", None)

# ---------------- Title ----------------
st.title("Ask PDF! 🚀 RAG with FAISS")
st.caption("OpenAI / Gemini / Vertex / HuggingFace embeddings + FAISS retrieval")

# ---------------- Top Controls ----------------
col1, col2, col3, col4 = st.columns(4)
with col1:
    uploaded_file = st.file_uploader("Upload PDF or TXT", type=["pdf", "txt"])

available_providers = [p for p, m in EMBED_MODELS.items() if m]
if not available_providers:
    available_providers = ["OpenAI"]

with col2:
    provider = st.selectbox("Embedding Provider", available_providers)

with col3:
    if provider == "Gemini":
        if EMBED_MODELS["Gemini"]:
            model = st.selectbox("Embedding Model", list(EMBED_MODELS[provider].keys()), key=f"embed_model_{provider}")
        else:
            st.write("Gemini embeddings: not available in this project")
            model = None
    elif provider == "Vertex":
        if EMBED_MODELS["Vertex"]:
            model = st.selectbox("Embedding Model (Vertex)", list(EMBED_MODELS[provider].keys()), key=f"embed_model_{provider}")
        else:
            st.write("Vertex embeddings: not available (ensure GCP creds/project/location are set in secrets)")
            model = None
    else:
        model = st.selectbox("Embedding Model", list(EMBED_MODELS[provider].keys()), key=f"embed_model_{provider}")

# Answer Provider controls
answer_providers = []
if "OpenAI" in EMBED_MODELS and EMBED_MODELS["OpenAI"]:
    answer_providers.append("OpenAI")
if "Gemini" in EMBED_MODELS and EMBED_MODELS["Gemini"]:
    answer_providers.append("Gemini")
if not answer_providers:
    answer_providers = ["None"]

if provider == "OpenAI" and "OpenAI" in answer_providers:
    default_ans = "OpenAI"
elif provider == "Gemini" and "Gemini" in answer_providers:
    default_ans = "Gemini"
elif "OpenAI" in answer_providers:
    default_ans = "OpenAI"
else:
    default_ans = answer_providers[0]

with col4:
    answer_provider = st.selectbox("Answer Provider", answer_providers, index=answer_providers.index(default_ans))
    if answer_provider == "OpenAI":
        openai_chat_model = st.selectbox("OpenAI chat model", OPENAI_CHAT_MODELS, key="openai_chat_model")
        gemini_chat_model = None
    elif answer_provider == "Gemini":
        gemini_chat_model = st.selectbox("Gemini answer model", GEMINI_CHAT_CANDIDATES, index=0, key="gemini_chat_model")
        openai_chat_model = None
    else:
        openai_chat_model = None
        gemini_chat_model = None

# ---------------- Sidebar Controls for generation, chunking & UI toggles ----------------
with st.sidebar:
    st.header("Generation Parameters")
    temperature = st.slider("Temperature", 0.0, 2.0, 0.6, 0.01)
    max_tokens = st.slider("Gemini/OpenAI max output tokens", 32, 4096, 512, 8)
    top_p = st.slider("Top P", 0.0, 1.0, 1.0, 0.01)
    frequency_penalty = st.slider("Frequency Penalty (OpenAI)", 0.0, 2.0, 0.0, 0.01)
    presence_penalty = st.slider("Presence Penalty (OpenAI)", 0.0, 2.0, 0.0, 0.01)
    st.divider()
    st.subheader("Gemini Advanced")
    gemini_max_rounds = st.slider("Auto‑continue rounds (Gemini)", 0, 8, 2, 1)
    gemini_context_cap_chars = st.slider("Context cap (chars)", 4000, 60000, 20000, 1000)
    gemini_est_token_divisor = st.slider("Approx chars per token (Gemini estimate)", 2, 8, 4, 1)
    reserve_output_tokens = st.slider("Reserve output tokens (approx)", 64, 2048, 512, 32)
    relax_safety = st.checkbox("Relax Gemini safety (BLOCK_NONE)", value=False)
    enable_fallback = st.checkbox("Enable fallback models", value=True)
    fallback_order_input = st.text_input(
        "Fallback chain (comma separated)",
        ",".join([m for m in GEMINI_CHAT_CANDIDATES if m != gemini_chat_model]) if 'gemini_chat_model' in locals() else "",
    )
    st.divider()
    st.subheader("Chunking")
    chunk_size = st.slider("Chunk size (tokens)", 200, 1500, 500, 50)
    chunk_overlap = st.slider("Chunk overlap (tokens)", 0, 500, 100, 10)
    st.caption("Adjust then re-upload to re‑chunk.")
    st.divider()
    st.subheader("UI")
    show_matching_chunks = st.checkbox("Show 'Top Matching Chunks' column", value=False)
    st.divider()
    # Note: debug toggle moved to Admin page; main app reads ss["enable_debug"].

# ---------------- Reset on new upload ----------------
if uploaded_file is not None:
    file_id = uploaded_file.name + str(uploaded_file.size)
    if file_id != ss.last_file_name:
        ss.chunks = []
        ss.model_embeddings.clear()
        ss.model_indexes.clear()
        ss.pdf_loaded = False
        ss.last_file_name = file_id

# ---------------- Local chunking fallback ----------------
def chunk_text_local(text: str, size: int, overlap: int, encoding_name="cl100k_base") -> List[str]:
    enc = tiktoken.get_encoding(encoding_name)
    toks = enc.encode(text or "")
    n = len(toks)
    out = []
    start = 0
    while start < n:
        end = min(start + size, n)
        piece = toks[start:end]
        if piece:
            out.append(enc.decode(piece))
        advance = max(1, size - overlap)
        start += advance
    return out

def robust_pdf_text_local(file) -> str:
    rdr = PdfReader(file)
    parts = []
    for p in rdr.pages:
        try:
            txt = p.extract_text() or ""
        except Exception:
            txt = ""
        if txt:
            parts.append(txt)
    return "\n".join(parts)

# ---------------- Load & Chunk ----------------
if uploaded_file and not ss.pdf_loaded:
    with st.spinner("Reading & chunking document..."):
        if uploaded_file.type == "application/pdf":
            raw_text = robust_pdf_text_local(uploaded_file)
        else:
            raw_text = uploaded_file.read().decode("utf-8", errors="replace")
        ss.chunks = chunk_text_local(raw_text, size=chunk_size, overlap=chunk_overlap)
    ss.pdf_loaded = True

current_key = (provider, model)

# ---------------- Bind EMBED_FUNCS (provider wrappers) ----------------
EMBED_FUNCS = {
    "OpenAI": lambda texts, name: openai_embed_texts(texts, name, openai_api_key),
    "Gemini": lambda texts, name: gemini_embed_helper(texts, name, gemini_api_key),
    "Vertex": lambda texts, name: vertex_embed_helper(texts, name, gcp_sa_info, gcp_project, gcp_location),
    # Use the hf_embed helper and pass the HF token. If hf_embed_helper is not present, return None.
    "HuggingFace": (lambda texts, name: hf_embed_helper(texts, name, huggingface_api_token)) if 'hf_embed_helper' in globals() else None,
}

# ---------------- Build embeddings & index when needed ----------------
if ss.pdf_loaded and ss.chunks and provider and model:
    if provider == "Gemini" and not EMBED_MODELS["Gemini"]:
        st.warning("Gemini embedding model not available for this project — choose another provider.")
    elif provider == "Vertex" and not EMBED_MODELS["Vertex"]:
        st.warning("Vertex embedding model not available — ensure GCP creds/project/location are set.")
    else:
        if current_key not in ss.model_embeddings:
            build_embeddings_and_index(
                ss,
                provider,
                model,
                EMBED_FUNCS,
                EMBED_MODELS,
                chunk_size,
                chunk_overlap,
                gemini_api_key=gemini_api_key,
                huggingface_api_token=huggingface_api_token,
            )

# ---------------- Debug info (read from Admin toggle in session_state) ----------------
enable_debug = ss.get("enable_debug", False)
if enable_debug:
    try:
        st.subheader("Debug: embeddings/index summary")
        st.write("Detected embed model lists (session):")
        st.write("detected_openai_embeds:", ss.get("detected_openai_embeds"))
        st.write("detected_gemini_embeds:", ss.get("detected_gemini_embeds"))
        st.write("detected_vertex_embeds:", ss.get("detected_vertex_embeds"))
        me = ss.get("model_embeddings", {})
        mi = ss.get("model_indexes", {})
        st.write("model_embeddings keys:", list(me.keys()))
        st.write("model_indexes keys:", list(mi.keys()))
        if current_key in me:
            st.write(f"{current_key} embedding shape:", getattr(me[current_key], "shape", None))
    except Exception:
        pass

# ---------------- Answer provider validation ----------------
answer_ok = True
answer_missing_reasons = []

if answer_provider == "OpenAI":
    if not openai_api_key:
        answer_ok = False
        answer_missing_reasons.append("OpenAI API key missing in st.secrets['openai']['api_key'].")
    if not openai_chat_model:
        answer_ok = False
        answer_missing_reasons.append("OpenAI chat model not selected.")
elif answer_provider == "Gemini":
    if not gemini_api_key:
        answer_ok = False
        answer_missing_reasons.append("Gemini API key missing in st.secrets['gemini']['api_key'].")
    if not gemini_chat_model:
        answer_ok = False
        answer_missing_reasons.append("Gemini chat model not selected.")
else:
    answer_ok = False
    answer_missing_reasons.append("No answer provider available/selected.")

if not answer_ok:
    st.error("Answer provider not configured correctly:")
    for r in answer_missing_reasons:
        st.write(f"- {r}")
    st.info("Select a valid Answer Provider and ensure the corresponding API key + chat model are configured in Streamlit secrets.")
else:
    # ---------------- Run retrieval UI (delegated) ----------------
    run_retrieval_ui(
        ss=ss,
        provider=provider,
        model=model,
        EMBED_FUNCS=EMBED_FUNCS,
        EMBED_MODELS=EMBED_MODELS,
        openai_api_key=openai_api_key,
        openai_chat_model=openai_chat_model if 'openai_chat_model' in locals() else None,
        gemini_api_base=GEMINI_API_BASE,
        gemini_api_key=gemini_api_key,
        gemini_chat_model=gemini_chat_model if 'gemini_chat_model' in locals() else None,
        GEMINI_CHAT_CANDIDATES=GEMINI_CHAT_CANDIDATES,
        hf_api_token=huggingface_api_token,
        show_matching_chunks=show_matching_chunks,
        debug=enable_debug,
    )

st.markdown("---")
st.markdown("""
<div style='text-align: center; font-size: 0.9rem; margin-top: 2rem;'>
    <br><br>
    © 2026 CX Data & Analytics LLC
</div>
""", unsafe_allow_html=True)
