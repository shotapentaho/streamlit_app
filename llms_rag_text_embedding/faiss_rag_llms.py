"""
Ask PDF! 🚀  (v13)
RAG over PDF/TXT using FAISS + multiple embedding providers (OpenAI / Gemini / HuggingFace)
Gemini answer generation with:
 - Auto‑continuation for MAX_TOKENS
 - Multi‑model fallback chain
 - Safety filter relaxation toggle
 - Context length / token budget management
 - Detailed debug meta (finishReason, safetyRatings, promptFeedback, usage deltas, raw last candidate)
 - Better empty-output diagnostics (why no text, suggestions)
"""

import streamlit as st
import openai
import faiss
import numpy as np
from pypdf import PdfReader
import requests
from ui_theme import apply_theme
import tiktoken
import json
import math
from typing import List, Dict, Any, Tuple, Optional

# ---------------- UI & Theme ----------------
st.set_page_config(page_title="Ask PDF! 🚀 RAG with FAISS (v13)", layout="wide")
apply_theme()

st.markdown(
    """
<style>
#MainMenu {visibility: hidden;}
</style>
""",
    unsafe_allow_html=True
)

# ---------------- Secrets / Keys ----------------
openai_api_key = st.secrets["openai"]["api_key"]
gemini_api_key = st.secrets["gemini"]["api_key"]
huggingface_api_token = st.secrets["huggingface"]["api_token"]

# ---------------- Model Registries ----------------
HF_MODELS = {
    "BAAI/bge-large-en-v1.5": "BAAI/bge-large-en-v1.5",
    "BAAI/bge-small-en-v1.5": "BAAI/bge-small-en-v1.5",
}

EMBED_MODELS = {
    "OpenAI": {
        "text-embedding-ada-002": "text-embedding-ada-002",
        "text-embedding-3-large": "text-embedding-3-large",
        "text-embedding-3-small": "text-embedding-3-small"
    },
    "Gemini": {
        "gemini-embedding-001": "gemini-embedding-001"
    },
    "HuggingFace": HF_MODELS
}

OPENAI_CHAT_MODELS = [
    "gpt-4",
    "gpt-4-turbo",
    "gpt-3.5-turbo"
]

GEMINI_CHAT_CANDIDATES = [
    "gemini-2.5-pro",
    "gemini-2.0-flash",
    "gemini-1.5-flash-8b"
]

GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"

# ---------------- Session State ----------------
ss = st.session_state
ss.setdefault("chunks", [])
ss.setdefault("model_embeddings", {})  # (provider,model) -> np.ndarray
ss.setdefault("model_indexes", {})     # (provider,model) -> faiss.Index
ss.setdefault("pdf_loaded", False)
ss.setdefault("last_file_name", None)

# ---------------- Title ----------------
st.title("Ask PDF: Semantic Q&A with RAG 🚀 (v13)")
st.caption("OpenAI / Gemini / HuggingFace embeddings + FAISS retrieval + Gemini continuation & fallback logic")

# ---------------- Top Controls ----------------
col1, col2, col3 = st.columns(3)
with col1:
    uploaded_file = st.file_uploader("Upload PDF or TXT", type=["pdf", "txt"])
with col2:
    provider = st.selectbox("Embedding Provider", list(EMBED_MODELS.keys()))
with col3:
    model = st.selectbox(
        "Embedding Model",
        list(EMBED_MODELS[provider].keys()),
        key=f"embed_model_{provider}"
    )

if provider == "OpenAI":
    openai_chat_model = st.selectbox("OpenAI chat model", OPENAI_CHAT_MODELS, key="openai_chat_model")
    gemini_chat_model = None
elif provider == "Gemini":
    openai_chat_model = None
    gemini_chat_model = st.selectbox("Gemini answer model", GEMINI_CHAT_CANDIDATES, index=0, key="gemini_chat_model")
else:
    openai_chat_model = None
    gemini_chat_model = None

# ---------------- Sidebar Controls ----------------
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
    gemini_est_token_divisor = st.slider("Approx chars per token (Gemini estimate)", 2, 8, 4, 1,
                                         help="Used to reserve output tokens by trimming context.")
    reserve_output_tokens = st.slider("Reserve output tokens (approx)", 64, 2048, 512, 32,
                                      help="We trim context so that prompt tokens + reserve ≤ model limit (rough).")
    relax_safety = st.checkbox("Relax Gemini safety (BLOCK_NONE)", value=False)
    enable_fallback = st.checkbox("Enable fallback models", value=True)
    fallback_order_input = st.text_input(
        "Fallback chain (comma separated)", 
        ",".join([m for m in GEMINI_CHAT_CANDIDATES if m != gemini_chat_model]),
        help="Models tried in order if primary returns no text. Must be valid Gemini model IDs."
    )
    st.caption("Fallback triggers only if zero text after retries.")
    st.divider()
    st.subheader("Chunking")
    chunk_size = st.slider("Chunk size (tokens)", 200, 1500, 500, 50)
    chunk_overlap = st.slider("Chunk overlap (tokens)", 0, 500, 100, 10)
    st.caption("Adjust then re-upload to re‑chunk.")
    st.divider()
    show_debug_embeddings = st.checkbox("Show embeddings shape/debug", value=False)

# ---------------- Reset on new upload ----------------
if uploaded_file is not None:
    file_id = uploaded_file.name + str(uploaded_file.size)
    if file_id != ss.last_file_name:
        ss.chunks = []
        ss.model_embeddings.clear()
        ss.model_indexes.clear()
        ss.pdf_loaded = False
        ss.last_file_name = file_id

# ---------------- Helpers ----------------
def chunk_text(text: str, size: int, overlap: int, encoding_name="cl100k_base") -> List[str]:
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
        # guard against infinite loops if size <= overlap
        advance = max(1, size - overlap)
        start += advance
    return out

def openai_embed_texts(texts: List[str], embedding_model: str):
    try:
        client = openai.OpenAI(api_key=openai_api_key)
        response = client.embeddings.create(input=texts, model=embedding_model)
        arr = np.array([d.embedding for d in response.data], dtype="float32")
        if arr.ndim == 1:
            arr = arr[None, :]
        return arr
    except Exception as e:
        st.error(f"OpenAI embedding error: {e}")
        return None

def gemini_embed_texts(texts: List[str], embedding_model: str):
    api_url = f"{GEMINI_API_BASE}/models/{embedding_model}:embedContent?key={gemini_api_key}"
    headers = {"Content-Type": "application/json"}
    embs: List[List[float]] = []
    prog = st.progress(0, text="Gemini embedding...")
    for i, txt in enumerate(texts):
        data = {"content": {"parts": [{"text": txt}]}}
        try:
            r = requests.post(api_url, headers=headers, json=data, timeout=60)
        except Exception as e:
            st.error(f"Gemini embedding network error: {e}")
            embs.append([0.0])
            continue
        if r.status_code != 200:
            st.warning(f"Gemini embedding error: {r.status_code}")
            embs.append([0.0])
        else:
            j = r.json()
            emb = j.get("embedding", {}).get("value") or j.get("embedding", {}).get("values") or []
            embs.append(emb if emb else [0.0])
        prog.progress((i + 1) / len(texts))
    prog.empty()
    arr = np.array(embs, dtype="float32")
    if arr.ndim == 1:
        arr = arr[None, :]
    if arr.ndim == 3:
        arr = arr.mean(axis=1)
    return arr

def hf_embed_texts(texts: List[str], model_name: str, fallback_dim: Optional[int] = None):
    api_url = f"https://api-inference.huggingface.co/models/{model_name}"
    headers = {"Authorization": f"Bearer {huggingface_api_token}", "Content-Type": "application/json"}
    out_vecs = []
    for t in texts:
        data = {"inputs": t}
        try:
            r = requests.post(api_url, headers=headers, json=data, timeout=120)
        except Exception as e:
            st.error(f"HuggingFace network error: {e}")
            vec = np.zeros(fallback_dim or 23, dtype="float32")
            out_vecs.append(vec)
            continue
        if r.status_code != 200:
            vec = np.zeros(fallback_dim or 23, dtype="float32")
            out_vecs.append(vec)
        else:
            j = r.json()
            if isinstance(j, list) and j and isinstance(j[0], list):
                arr = np.array(j, dtype="float32")
                out_vecs.append(arr.mean(axis=0))
            elif isinstance(j, list):
                out_vecs.append(np.array(j, dtype="float32"))
            else:
                out_vecs.append(np.zeros(fallback_dim or 23, dtype="float32"))
    arr = np.array(out_vecs, dtype="float32")
    if arr.ndim == 1:
        arr = arr[None, :]
    if arr.ndim == 3:
        arr = arr.mean(axis=1)
    return arr

EMBED_FUNCS = {
    "OpenAI": openai_embed_texts,
    "Gemini": gemini_embed_texts,
    "HuggingFace": None
}

def robust_pdf_text(file) -> str:
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
            raw_text = robust_pdf_text(uploaded_file)
        else:
            raw_text = uploaded_file.read().decode("utf-8", errors="replace")
        ss.chunks = chunk_text(raw_text, size=chunk_size, overlap=chunk_overlap)
        st.success(f"Chunked into {len(ss.chunks)} chunks (size={chunk_size}, overlap={chunk_overlap}).")
    ss.pdf_loaded = True

current_key = (provider, model)

# ---------------- Embeddings & Index ----------------
if ss.pdf_loaded and ss.chunks:
    if current_key not in ss.model_embeddings:
        with st.spinner(f"Embedding chunks with {provider} / {model}"):
            if provider == "HuggingFace":
                probe = hf_embed_texts([ss.chunks[0]], EMBED_MODELS["HuggingFace"][model])
                dim = probe.shape[1]
                EMBED_FUNCS["HuggingFace"] = lambda texts, name: hf_embed_texts(texts, name, fallback_dim=dim)
            embed_func = EMBED_FUNCS[provider]
            emb = embed_func(ss.chunks, EMBED_MODELS[provider][model])
            if emb is None:
                st.stop()
            if emb.ndim == 1:
                emb = emb[None, :]
            if emb.ndim == 3:
                emb = emb.mean(axis=1)
            emb = emb.astype("float32", copy=False)
            index = faiss.IndexFlatL2(emb.shape[1])
            index.add(emb)
            ss.model_embeddings[current_key] = emb
            ss.model_indexes[current_key] = index
        st.success("Embedding index ready.")
        if show_debug_embeddings:
            st.write("Embeddings shape:", ss.model_embeddings[current_key].shape)

# ---------------- Gemini Answer Logic (v13) ----------------
def approx_token_count(text: str, chars_per_token: int) -> int:
    return math.ceil(len(text) / max(1, chars_per_token))

def _get_finish_reason(gjson: Dict[str, Any]) -> str:
    try:
        return gjson["candidates"][0].get("finishReason", "")
    except Exception:
        return ""

def _get_safety(gjson: Dict[str, Any]) -> Any:
    try:
        return gjson["candidates"][0].get("safetyRatings", None)
    except Exception:
        return None

def _extract_text(gjson: Dict[str, Any]) -> str:
    try:
        cand = (gjson.get("candidates") or [])[0]
        parts = (cand.get("content") or {}).get("parts") or []
        out = [p.get("text", "") for p in parts if isinstance(p, dict) and p.get("text")]
        if out:
            return "\n".join(out).strip()
        if isinstance(cand.get("text"), str):
            return cand["text"].strip()
        return ""
    except Exception:
        return ""

def safe_json(txt: str) -> Any:
    try:
        return json.loads(txt)
    except Exception:
        return txt

def gemini_call(contents: List[Dict[str, Any]],
                model: str,
                gen_cfg: Dict[str, Any],
                safety_relaxed: bool) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    url = f"{GEMINI_API_BASE}/models/{model}:generateContent?key={gemini_api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": contents,
        "generationConfig": {
            "temperature": gen_cfg["temperature"],
            "maxOutputTokens": gen_cfg["maxOutputTokens"],
            "topP": gen_cfg["topP"],
            "frequencyPenalty": gen_cfg["frequencyPenalty"],
            "presencePenalty": gen_cfg["presencePenalty"],
            "responseMimeType": "text/plain"
        }
    }
    if safety_relaxed:
        payload["safetySettings"] = [
            {"category": c, "threshold": "BLOCK_NONE"}
            for c in [
                "HARM_CATEGORY_HATE_SPEECH",
                "HARM_CATEGORY_HARASSMENT",
                "HARM_CATEGORY_DANGEROUS_CONTENT",
                "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            ]
        ]
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=120)
    except Exception as e:
        return None, f"Network error: {e}"
    if r.status_code != 200:
        return None, f"HTTP {r.status_code}: {r.text[:400]}"
    return r.json(), None

def gemini_answer_pipeline(context: str,
                           question: str,
                           primary_model: str,
                           gen_cfg: Dict[str, Any],
                           max_rounds: int,
                           safety_relaxed: bool,
                           fallback_chain: List[str]) -> Tuple[str, Dict[str, Any]]:
    attempts: List[Dict[str, Any]] = []
    raw_tail = None
    accumulated = ""
    model_used_sequence = []

    def base_contents(ctx: str, q: str) -> List[Dict[str, Any]]:
        return [
            {
                "role": "user",
                "parts": [{
                    "text": (
                        "You are a concise assistant. Use ONLY the supplied context. "
                        "If answer not in context, say: I don't know based on the provided context."
                    )
                }]
            },
            {"role": "user", "parts": [{"text": f"Context:\n{ctx}\n\nQuestion: {q}"}]}
        ]

    chain = [primary_model] + [m for m in fallback_chain if m and m != primary_model]
    for chain_idx, model_id in enumerate(chain):
        model_used_sequence.append(model_id)
        # Fresh attempt for this model
        contents = base_contents(context, question)
        round_no = 0
        # First call
        resp_json, err = gemini_call(contents, model_id, gen_cfg, safety_relaxed)
        attempt_meta = {
            "model": model_id,
            "stage": "initial",
            "error": err,
        }
        if resp_json:
            attempt_meta.update({
                "finishReason": _get_finish_reason(resp_json),
                "safetyRatings": _get_safety(resp_json),
                "promptFeedback": resp_json.get("promptFeedback"),
                "usage": resp_json.get("usageMetadata")
            })
            txt = _extract_text(resp_json)
            if txt:
                accumulated += txt
        attempts.append(attempt_meta)
        raw_tail = resp_json

        # If we got text, proceed to continuation if MAX_TOKENS else done
        fr = attempt_meta.get("finishReason", "")
        # Continuation loop
        while resp_json and fr == "MAX_TOKENS" and round_no < max_rounds:
            round_no += 1
            contents = [
                {"role": "user", "parts": [{"text": f"Context:\n{context}\n\nQuestion: {question}"}]},
                {"role": "model", "parts": [{"text": accumulated}]},
                {"role": "user", "parts": [{"text": "Continue. Do NOT repeat previous text."}]}
            ]
            resp_json, err = gemini_call(contents, model_id, gen_cfg, safety_relaxed)
            cont_meta = {
                "model": model_id,
                "stage": f"continue_{round_no}",
                "error": err
            }
            if resp_json:
                cont_meta.update({
                    "finishReason": _get_finish_reason(resp_json),
                    "safetyRatings": _get_safety(resp_json),
                    "usage": resp_json.get("usageMetadata")
                })
                txt = _extract_text(resp_json)
                if txt:
                    accumulated += txt
                fr = cont_meta.get("finishReason", "")
            attempts.append(cont_meta)
            raw_tail = resp_json
            if not resp_json or err:  # network or HTTP error break
                break

        if accumulated:
            break  # success with this model
        else:
            # If no text AND not last model, shrink context for next fallback
            context = context[-8000:] if len(context) > 8000 else context

    debug_meta = {
        "attempts": attempts,
        "models_tried": model_used_sequence,
        "final_finishReason": _get_finish_reason(raw_tail) if raw_tail else None,
        "final_safetyRatings": _get_safety(raw_tail) if raw_tail else None,
        "raw_tail": raw_tail
    }

    if not accumulated:
        reason = debug_meta.get("final_finishReason")
        if reason == "SAFETY":
            accumulated = "Response blocked by Gemini safety filters (try enabling 'Relax safety')."
        else:
            accumulated = ""
    return accumulated.strip(), debug_meta

# ---------------- Retrieval & QA ----------------
if ss.pdf_loaded and ss.chunks and current_key in ss.model_indexes:
    st.info(f"Embeddings ready: {provider} / {model}")
    query = st.text_input("Ask a question about the document:")
    if query:
        # Retrieval params (dynamic)
        corpus_size = len(ss.chunks)
        with st.sidebar:
            st.subheader("Retrieval")
            top_k = st.slider("Top K", 1, min(100, corpus_size), min(10, corpus_size), 1)
            preview_chars = st.slider("Chunk preview chars", 100, 4000, 800, 50)

        # Prepare query embedding
        if provider == "HuggingFace":
            emb_dim = ss.model_embeddings[current_key].shape[1]
            embed_func = lambda texts, name: hf_embed_texts(texts, name, fallback_dim=emb_dim)
        else:
            embed_func = EMBED_FUNCS[provider]

        q_emb = embed_func([query], EMBED_MODELS[provider][model])
        if q_emb is None:
            st.stop()
        if q_emb.ndim == 1:
            q_emb = q_emb[None, :]
        if q_emb.ndim == 3:
            q_emb = q_emb.mean(axis=1)
        q_emb = q_emb.astype("float32", copy=False)

        # Search
        index = ss.model_indexes[current_key]
        D, I = index.search(q_emb, k=min(top_k, corpus_size))
        seen = set()
        ordered_idx = []
        for idx in I[0]:
            if idx == -1: continue
            if idx in seen: continue
            seen.add(idx)
            ordered_idx.append(idx)
        retrieved_chunks = [ss.chunks[i] for i in ordered_idx]

        left, right = st.columns(2)
        with left:
            st.subheader("Top Matching Chunks")
            for i, ch in enumerate(retrieved_chunks, 1):
                st.markdown(f"**Chunk {i} (#{ordered_idx[i-1]})**")
                st.write(ch[:preview_chars] + ("..." if len(ch) > preview_chars else ""))
                st.divider()

        with right:
            context = "\n\n".join(retrieved_chunks)
            if provider == "OpenAI" and openai_chat_model:
                st.subheader("RAG Answer (OpenAI)")
                try:
                    client = openai.OpenAI(api_key=openai_api_key)
                    messages = [
                        {"role": "system", "content": "Answer ONLY from context. If insufficient, say you don't know."},
                        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
                    ]
                    resp = client.chat.completions.create(
                        model=openai_chat_model,
                        messages=messages,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        top_p=top_p,
                        frequency_penalty=frequency_penalty,
                        presence_penalty=presence_penalty
                    )
                    st.write(resp.choices[0].message.content.strip())
                except Exception as e:
                    st.error(f"OpenAI error: {e}")

            elif provider == "Gemini" and gemini_chat_model:
                st.subheader("RAG Answer (Gemini)")
                # Trim context to cap & reserve output space (approximate)
                context_trimmed = context
                approx_prompt_tokens = approx_token_count(context_trimmed, gemini_est_token_divisor)
                desired_output = max_tokens
                # If we want to reserve 'reserve_output_tokens', reduce context until requirement satisfied
                # This is a rough heuristic; actual tokenization differs.
                while (approx_prompt_tokens + reserve_output_tokens) > 8192 and len(context_trimmed) > 2000:
                    # remove oldest portion
                    cut = int(len(context_trimmed) * 0.15)
                    context_trimmed = context_trimmed[cut:]
                    approx_prompt_tokens = approx_token_count(context_trimmed, gemini_est_token_divisor)
                # Hard char cap
                if len(context_trimmed) > gemini_context_cap_chars:
                    context_trimmed = context_trimmed[-gemini_context_cap_chars:]

                gen_cfg = {
                    "temperature": temperature,
                    "maxOutputTokens": max_tokens,
                    "topP": top_p,
                    "frequencyPenalty": frequency_penalty,
                    "presencePenalty": presence_penalty
                }
                fallback_chain = []
                if enable_fallback:
                    # parse fallback input
                    user_chain = [m.strip() for m in fallback_order_input.split(",") if m.strip()]
                    fallback_chain = [m for m in user_chain if m in GEMINI_CHAT_CANDIDATES and m != gemini_chat_model]

                with st.spinner("Gemini answering..."):
                    answer, meta = gemini_answer_pipeline(
                        context_trimmed,
                        query,
                        gemini_chat_model,
                        gen_cfg,
                        gemini_max_rounds,
                        relax_safety,
                        fallback_chain
                    )
                if answer:
                    st.write(answer)
                else:
                    st.warning("No text returned by Gemini. See debug below for reasons / suggestions.")
                    st.info(
                        "Try: 1) Increase max tokens. 2) Reduce chunk preview or Top K. "
                        "3) Relax safety. 4) Use a Flash model. 5) Lower temperature."
                    )
                with st.expander("Gemini debug meta"):
                    st.json(meta)
                with st.expander("Context sent to Gemini (trimmed)"):
                    st.write(context_trimmed[:8000] + ("..." if len(context_trimmed) > 8000 else ""))

            elif provider == "HuggingFace":
                st.subheader(f"Retrieved Context ({model})")
                st.write(context)
                st.info("Add an HF text-generation integration or copy context to another LLM.")

else:
    if not uploaded_file:
        st.info("Upload a PDF or TXT to begin.")
    elif not ss.chunks:
        st.warning("No chunks were produced (maybe empty file?).")


st.markdown("---")

# --- TESTIMONIAL / FOOTER ---
st.markdown("""
<div style='text-align: center; font-size: 0.9rem; margin-top: 2rem;'>
    <br><br>
    © 2025 CX Data & Analytics LLC
</div>
""", unsafe_allow_html=True)


st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)


