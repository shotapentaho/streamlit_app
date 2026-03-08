"""
Embedding provider helpers extracted from app.py.

Provides provider-specific embedding wrappers that the main app calls.
Functions:
- gemini_embed_texts(texts, embedding_model, gemini_api_key)
- vertex_embed_texts_ui(texts, model_id, gcp_sa_info, gcp_project, gcp_location)
- hf_embed_texts(texts, model_name, huggingface_api_token, fallback_dim=None)

These use detect_embedding_model's vertex_embed_texts and openai helper.
"""
from typing import List, Optional
import json
import requests
import numpy as np
import streamlit as st

from detect_embedding_model import GEMINI_API_BASES, vertex_embed_texts as _vertex_embed_texts
from detect_embedding_model import openai_embed_texts

def gemini_embed_texts(texts: List[str], embedding_model: str, gemini_api_key: str) -> Optional[np.ndarray]:
    """
    Robust Gemini embedding helper (UI-aware).
    """
    if not embedding_model:
        st.error("No Gemini embedding model configured for this project.")
        return None

    endpoints = [":embedText", ":embed", ":embedContent"]
    headers = {"Content-Type": "application/json"}
    embs: List[List[float]] = []
    prog = st.progress(0, text="Gemini embedding...")
    for i, txt in enumerate(texts):
        success = False
        last_status = None
        last_text = ""
        last_url = None
        last_payload = None

        for base in GEMINI_API_BASES:
            base_url = f"{base}/models/{embedding_model}"
            for ep in endpoints:
                url = f"{base_url}{ep}?key={gemini_api_key}"
                last_url = url

                if ep == ":embedText":
                    payload_variants = [
                        {"text": txt},
                        {"content": [{"text": txt}]},
                        {"content": {"text": txt}},
                    ]
                else:
                    payload_variants = [
                        {"content": {"parts": [{"text": txt}]}}
                    ]

                for payload in payload_variants:
                    last_payload = payload
                    try:
                        r = requests.post(url, headers=headers, json=payload, timeout=60)
                    except Exception as e:
                        last_text = f"Network error for {url}: {e}"
                        last_status = None
                        continue

                    last_status = r.status_code
                    if r.status_code != 200:
                        last_text = r.text or "<empty body>"
                        continue

                    try:
                        j = r.json()
                    except Exception:
                        last_text = f"Non-JSON response from {url}: {r.text[:1000]}"
                        continue

                    # Try multiple JSON shapes for embedding
                    emb = []
                    if isinstance(j.get("embedding"), dict):
                        emb = j["embedding"].get("value") or j["embedding"].get("values") or []
                    elif isinstance(j.get("embeddings"), list) and j["embeddings"]:
                        first = j["embeddings"][0]
                        emb = first if isinstance(first, list) else first.get("values") or first.get("embedding") or []
                    elif isinstance(j, list) and j and isinstance(j[0], (list, float, int)):
                        emb = j[0]
                    elif isinstance(j.get("data"), list) and j["data"]:
                        first = j["data"][0]
                        if isinstance(first, dict) and "embedding" in first:
                            emb = first.get("embedding") or first.get("embedding", {}).get("value") or []

                    if emb and any(x is not None for x in emb):
                        try:
                            embs.append(list(map(float, emb)))
                            success = True
                            break
                        except Exception:
                            last_text = "Embedding present but could not coerce to floats"
                            continue
                    else:
                        last_text = f"No embedding in JSON from {url}; keys: {list(j.keys()) if isinstance(j, dict) else 'non-dict'}"
                        continue

                if success:
                    break
            if success:
                break

        if not success:
            st.warning(
                f"Gemini embedding failed for chunk {i} (last status={last_status})\n"
                f"Last URL: {last_url}\n"
                f"Last payload preview: {json.dumps(last_payload)[:1000] if last_payload is not None else 'N/A'}\n"
                f"Last response preview: {str(last_text)[:1000]}"
            )
            embs.append([0.0])
        prog.progress((i + 1) / len(texts))
    prog.empty()

    arr = np.array(embs, dtype="float32")
    if arr.ndim == 1:
        arr = arr[None, :]
    if arr.ndim == 3:
        arr = arr.mean(axis=1)
    return arr

def vertex_embed_texts_ui(texts: List[str], model_id: str, gcp_sa_info: dict, gcp_project: str, gcp_location: str) -> Optional[np.ndarray]:
    """
    UI wrapper for vertex_embed_texts: canonicalizes region and displays friendly errors.
    """
    if not gcp_sa_info or not gcp_project or not gcp_location:
        st.error("Vertex embedding requires GCP service account, project and location in Streamlit secrets under `gcp`.")
        return None

    region = gcp_location
    if gcp_location.endswith(("-a", "-b", "-c")):
        region = gcp_location.rsplit("-", 1)[0]

    arr = _vertex_embed_texts(texts, model_id, gcp_sa_info, gcp_project, region)
    if arr is None:
        st.error("Vertex embedding call failed. Check service account, project, location, and model id.")
    return arr

def hf_embed_texts(texts: List[str], model_name: str, huggingface_api_token: str, fallback_dim: Optional[int] = None) -> Optional[np.ndarray]:
    """
    HuggingFace inference wrapper returning numpy array.
    """
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
