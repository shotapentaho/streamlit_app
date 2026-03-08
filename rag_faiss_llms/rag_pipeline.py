"""
RAG pipeline and UI remainder extracted from app.py.

This module contains:
- build_embeddings_and_index(...)  -> builds embeddings and FAISS index for chunks
- gemini_answer_pipeline(...)     -> Gemini answer orchestration
- run_retrieval_ui(...)           -> retrieval UI (with optional debug)

This version fixes the missing export by including build_embeddings_and_index.
It also keeps the debug-capable run_retrieval_ui function used by app.py.
"""
from typing import List, Dict, Any, Tuple, Optional
import math
import json
import requests
import numpy as np
import faiss
import streamlit as st
import openai

# Import chunking utilities if available (app also has local fallbacks)
try:
    from chunking import chunk_text, robust_pdf_text
except Exception:
    chunk_text = None
    robust_pdf_text = None


# ---------------- Embedding / Index helpers ----------------
def build_embeddings_and_index(
    ss: st.session_state,
    provider: str,
    model: str,
    EMBED_FUNCS: Dict[str, Any],
    EMBED_MODELS: Dict[str, Dict[str, str]],
    chunk_size: int,
    chunk_overlap: int,
    gemini_api_key: Optional[str] = None,
    huggingface_api_token: Optional[str] = None,
) -> None:
    """
    Embed ss.chunks (assumed populated) with the specified provider/model and store
    embeddings and a faiss.Index into ss.model_embeddings and ss.model_indexes.

    This mirrors the embedding/indexing logic used in the app.
    """
    if not ss.get("pdf_loaded") or not ss.get("chunks"):
        return

    current_key = (provider, model)

    # validation
    if provider == "Gemini" and not EMBED_MODELS.get("Gemini"):
        st.warning("Gemini embedding model not available for this project — choose another provider.")
        return

    # Already indexed
    if current_key in ss.get("model_embeddings", {}):
        return

    with st.spinner(f"Embedding chunks with {provider} / {model}"):
        # If HF, we may need a probe step (handled by provider wrapper elsewhere)
        if provider == "HuggingFace":
            probe = EMBED_FUNCS["HuggingFace"]([ss.chunks[0]], EMBED_MODELS["HuggingFace"][model])
            dim = probe.shape[1]
            # keep existing HF wrapper; (app may set EMBED_FUNCS accordingly)

        embed_func = EMBED_FUNCS.get(provider)
        if not embed_func:
            st.error(f"No embed function for provider {provider}")
            return

        emb = embed_func(ss.chunks, EMBED_MODELS[provider][model])
        if emb is None:
            st.stop()

        if emb.ndim == 1:
            emb = emb[None, :]
        if emb.ndim == 3:
            emb = emb.mean(axis=1)
        emb = emb.astype("float32", copy=False)

        try:
            index = faiss.IndexFlatL2(emb.shape[1])
            index.add(emb)
        except Exception as e:
            st.error(f"FAISS index build error: {e}")
            raise

        # persist
        ss.model_embeddings[current_key] = emb
        ss.model_indexes[current_key] = index


# ---------------- Gemini answer logic & helpers ----------------
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


def gemini_call(
    contents: List[Dict[str, Any]],
    model: str,
    gen_cfg: Dict[str, Any],
    safety_relaxed: bool,
    gemini_api_base: str,
    gemini_api_key: str,
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    url = f"{gemini_api_base}/models/{model}:generateContent?key={gemini_api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": contents,
        "generationConfig": {
            "temperature": gen_cfg["temperature"],
            "maxOutputTokens": gen_cfg["maxOutputTokens"],
            "topP": gen_cfg["topP"],
            "frequencyPenalty": gen_cfg["frequencyPenalty"],
            "presencePenalty": gen_cfg["presencePenalty"],
            "responseMimeType": "text/plain",
        },
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
    try:
        return r.json(), None
    except Exception as e:
        return None, f"Invalid JSON response: {e}"


def gemini_answer_pipeline(
    context: str,
    question: str,
    primary_model: str,
    gen_cfg: Dict[str, Any],
    max_rounds: int,
    safety_relaxed: bool,
    fallback_chain: List[str],
    gemini_api_base: str,
    gemini_api_key: str,
) -> Tuple[str, Dict[str, Any]]:
    attempts: List[Dict[str, Any]] = []
    raw_tail = None
    accumulated = ""
    model_used_sequence = []

    def base_contents(ctx: str, q: str) -> List[Dict[str, Any]]:
        return [
            {
                "role": "user",
                "parts": [
                    {
                        "text": (
                            "You are a concise assistant. Use ONLY the supplied context. "
                            "If answer not in context, say: I don't know based on the provided context."
                        )
                    }
                ],
            },
            {"role": "user", "parts": [{"text": f"Context:\n{ctx}\n\nQuestion: {q}"}]},
        ]

    chain = [primary_model] + [m for m in fallback_chain if m and m != primary_model]
    for chain_idx, model_id in enumerate(chain):
        model_used_sequence.append(model_id)
        contents = base_contents(context, question)
        round_no = 0
        resp_json, err = gemini_call(contents, model_id, gen_cfg, safety_relaxed, gemini_api_base, gemini_api_key)
        attempt_meta = {"model": model_id, "stage": "initial", "error": err}
        if resp_json:
            attempt_meta.update(
                {
                    "finishReason": _get_finish_reason(resp_json),
                    "safetyRatings": _get_safety(resp_json),
                    "promptFeedback": resp_json.get("promptFeedback"),
                    "usage": resp_json.get("usageMetadata"),
                }
            )
            txt = _extract_text(resp_json)
            if txt:
                accumulated += txt
        attempts.append(attempt_meta)
        raw_tail = resp_json

        fr = attempt_meta.get("finishReason", "")
        while resp_json and fr == "MAX_TOKENS" and round_no < max_rounds:
            round_no += 1
            contents = [
                {"role": "user", "parts": [{"text": f"Context:\n{context}\n\nQuestion: {question}"}]},
                {"role": "model", "parts": [{"text": accumulated}]},
                {"role": "user", "parts": [{"text": "Continue. Do NOT repeat previous text."}]},
            ]
            resp_json, err = gemini_call(contents, model_id, gen_cfg, safety_relaxed, gemini_api_base, gemini_api_key)
            cont_meta = {"model": model_id, "stage": f"continue_{round_no}", "error": err}
            if resp_json:
                cont_meta.update(
                    {
                        "finishReason": _get_finish_reason(resp_json),
                        "safetyRatings": _get_safety(resp_json),
                        "usage": resp_json.get("usageMetadata"),
                    }
                )
                txt = _extract_text(resp_json)
                if txt:
                    accumulated += txt
                fr = cont_meta.get("finishReason", "")
            attempts.append(cont_meta)
            raw_tail = resp_json
            if not resp_json or err:
                break

        if accumulated:
            break
        else:
            context = context[-8000:] if len(context) > 8000 else context

    debug_meta = {
        "attempts": attempts,
        "models_tried": model_used_sequence,
        "final_finishReason": _get_finish_reason(raw_tail) if raw_tail else None,
        "final_safetyRatings": _get_safety(raw_tail) if raw_tail else None,
        "raw_tail": raw_tail,
    }

    if not accumulated:
        reason = debug_meta.get("final_finishReason")
        if reason == "SAFETY":
            accumulated = "Response blocked by Gemini safety filters (try enabling 'Relax safety')."
        else:
            accumulated = ""
    return accumulated.strip(), debug_meta


# ---------------- Retrieval & QA UI (with debug) ----------------
def run_retrieval_ui(
    ss: st.session_state,
    provider: str,
    model: str,
    EMBED_FUNCS: Dict[str, Any],
    EMBED_MODELS: Dict[str, Dict[str, str]],
    openai_api_key: Optional[str],
    openai_chat_model: Optional[str],
    gemini_api_base: str,
    gemini_api_key: Optional[str],
    gemini_chat_model: Optional[str],
    GEMINI_CHAT_CANDIDATES: List[str],
    hf_api_token: Optional[str],
    default_top_k: int = 10,
    default_preview_chars: int = 800,
    chunk_preview_range: Tuple[int, int] = (100, 4000),
    show_matching_chunks: bool = False,
    debug: bool = False,
):
    """
    Renders the Retrieval & QA UI and handles query embedding, FAISS search, and answering.
    debug=True prints diagnostics to help troubleshoot embeddings/index/search/answers.
    """
    if not (ss.get("pdf_loaded") and ss.get("chunks") and (provider, model) in ss.get("model_indexes", {})):
        if not ss.get("chunks"):
            st.info("Upload / chunk a document to begin.")
        else:
            st.info("Embeddings not ready. Choose provider/model and embed the chunks first.")
        return

    st.info(f"Embeddings ready: {provider} / {model}")

    # Optional debug overview
    if debug:
        try:
            st.subheader("DEBUG: Embedding/index overview")
            me = ss.get("model_embeddings", {})
            mi = ss.get("model_indexes", {})
            st.write("model_embeddings keys:", list(me.keys()))
            st.write("model_indexes keys:", list(mi.keys()))
            key = (provider, model)
            if key in me:
                st.write(f"Embedding array shape for {key}:", getattr(me[key], "shape", None))
            if key in mi:
                idx = mi[key]
                try:
                    st.write(f"FAISS index ntotal: {idx.ntotal}")
                    st.write(f"FAISS index dim (d): {getattr(idx, 'd', 'unknown')}")
                except Exception:
                    st.write("FAISS index info not available")
        except Exception as e:
            st.write("Debug overview error:", e)

    query = st.text_input("Ask a question about the document:")
    if not query:
        return

    corpus_size = len(ss.chunks)
    with st.sidebar:
        st.subheader("Retrieval")
        top_k = st.slider("Top K", 1, min(100, corpus_size), min(default_top_k, corpus_size), 1)
        preview_chars = st.slider("Chunk preview chars", chunk_preview_range[0], chunk_preview_range[1], default_preview_chars, 50)

    # Prepare query embedding function
    if provider == "Gemini":
        if not EMBED_MODELS.get("Gemini"):
            st.error("Gemini embeddings unavailable for this project. Switch to another provider.")
            return
        embed_func = lambda texts, name: EMBED_FUNCS["Gemini"](texts, name)
    elif provider == "Vertex":
        if not EMBED_MODELS.get("Vertex"):
            st.error("Vertex embeddings unavailable (ensure GCP creds/project/location are set).")
            return
        embed_func = lambda texts, name: EMBED_FUNCS["Vertex"](texts, name)
    elif provider == "HuggingFace":
        embed_func = lambda texts, name: EMBED_FUNCS["HuggingFace"](texts, name)
    else:
        embed_func = EMBED_FUNCS[provider]

    # Embed the query
    q_emb = embed_func([query], EMBED_MODELS[provider][model])
    if q_emb is None:
        st.error("Query embedding failed (None returned). See provider logs or enable debug.")
        st.stop()

    if q_emb.ndim == 1:
        q_emb = q_emb[None, :]
    if q_emb.ndim == 3:
        q_emb = q_emb.mean(axis=1)
    q_emb = q_emb.astype("float32", copy=False)

    if debug:
        st.write("Query embedding shape:", q_emb.shape)
        idx = ss.model_indexes.get((provider, model))
        try:
            st.write("Index dim (d):", getattr(idx, "d", None))
            st.write("Index ntotal:", getattr(idx, "ntotal", None))
        except Exception:
            pass

    # Search
    index = ss.model_indexes[(provider, model)]
    try:
        D, I = index.search(q_emb, k=min(top_k, corpus_size))
    except Exception as e:
        st.error(f"FAISS search error: {e}")
        if debug:
            emb = ss.model_embeddings.get((provider, model))
            st.write("Indexed embedding shape:", getattr(emb, "shape", None))
            st.write("Query emb shape:", q_emb.shape)
        return

    seen = set()
    ordered_idx = []
    for idx_val in I[0]:
        if idx_val == -1:
            continue
        if idx_val in seen:
            continue
        seen.add(idx_val)
        ordered_idx.append(idx_val)
    retrieved_chunks = [ss.chunks[i] for i in ordered_idx]

    if debug:
        st.subheader("DEBUG: Search results")
        st.write("D (distances):", D)
        st.write("I (indices):", I)
        st.write("ordered_idx:", ordered_idx)
        st.write("retrieved_chunks count:", len(retrieved_chunks))

    # Layout: optional left column
    if show_matching_chunks:
        left, right = st.columns(2)
    else:
        left = None
        right = st.container()  # full-width container for the answer area

    if show_matching_chunks:
        with left:
            st.subheader("Top Matching Chunks")
            for i, ch in enumerate(retrieved_chunks, 1):
                st.markdown(f"**Chunk {i} (#{ordered_idx[i-1]})**")
                st.write(ch[:preview_chars] + ("..." if len(ch) > preview_chars else ""))
                st.divider()

    with right:
        context = "\n\n".join(retrieved_chunks)

        # ANSWER ROUTING: prefer explicit chat model selection (openai_chat_model or gemini_chat_model)
        if openai_chat_model:
            st.subheader("RAG Answer (OpenAI)")
            try:
                client = openai.OpenAI(api_key=openai_api_key)
                messages = [
                    {"role": "system", "content": "Answer ONLY from context. If insufficient, say you don't know."},
                    {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"},
                ]
                resp = client.chat.completions.create(
                    model=openai_chat_model,
                    messages=messages,
                    max_tokens=st.session_state.get("max_tokens", 512),
                    temperature=st.session_state.get("temperature", 0.6),
                    top_p=st.session_state.get("top_p", 1.0),
                    frequency_penalty=st.session_state.get("frequency_penalty", 0.0),
                    presence_penalty=st.session_state.get("presence_penalty", 0.0),
                )
                answer_text = resp.choices[0].message.content.strip()
                st.write(answer_text)
                if debug:
                    st.subheader("DEBUG: OpenAI response object")
                    st.write(resp)
            except Exception as e:
                st.error(f"OpenAI error: {e}")

        elif gemini_chat_model:
            st.subheader("RAG Answer (Gemini)")
            gemini_est_token_divisor = st.session_state.get("gemini_est_token_divisor", 4)
            reserve_output_tokens = st.session_state.get("reserve_output_tokens", 512)
            gemini_context_cap_chars = st.session_state.get("gemini_context_cap_chars", 20000)
            gemini_max_rounds = st.session_state.get("gemini_max_rounds", 2)
            relax_safety = st.session_state.get("relax_safety", False)
            enable_fallback = st.session_state.get("enable_fallback", True)

            context_trimmed = context
            approx_prompt_tokens = approx_token_count(context_trimmed, gemini_est_token_divisor)
            desired_output = st.session_state.get("max_tokens", 512)
            while (approx_prompt_tokens + reserve_output_tokens) > 8192 and len(context_trimmed) > 2000:
                cut = int(len(context_trimmed) * 0.15)
                context_trimmed = context_trimmed[cut:]
                approx_prompt_tokens = approx_token_count(context_trimmed, gemini_est_token_divisor)
            if len(context_trimmed) > gemini_context_cap_chars:
                context_trimmed = context_trimmed[-gemini_context_cap_chars:]

            gen_cfg = {
                "temperature": st.session_state.get("temperature", 0.6),
                "maxOutputTokens": st.session_state.get("max_tokens", 512),
                "topP": st.session_state.get("top_p", 1.0),
                "frequencyPenalty": st.session_state.get("frequency_penalty", 0.0),
                "presencePenalty": st.session_state.get("presence_penalty", 0.0),
            }

            fallback_chain = []
            if enable_fallback:
                user_chain = [m.strip() for m in st.session_state.get("fallback_order_input", "").split(",") if m.strip()]
                fallback_chain = [m for m in user_chain if m in GEMINI_CHAT_CANDIDATES and m != gemini_chat_model]

            with st.spinner("Gemini answering..."):
                answer, meta = gemini_answer_pipeline(
                    context_trimmed,
                    query,
                    gemini_chat_model,
                    gen_cfg,
                    gemini_max_rounds,
                    relax_safety,
                    fallback_chain,
                    gemini_api_base,
                    gemini_api_key or "",
                )
            if answer:
                st.write(answer)
            else:
                st.warning("No text returned by Gemini. See debug below for reasons / suggestions.")
                st.info(
                    "Try: 1) Increase max tokens. 2) Reduce chunk preview or Top K. "
                    "3) Relax safety. 4) Use a Flash model. 5) Lower temperature."
                )
            if debug:
                st.subheader("DEBUG: Gemini answer meta")
                try:
                    st.json(meta)
                except Exception:
                    st.write(meta)

        elif provider == "HuggingFace":
            st.subheader(f"Retrieved Context ({model})")
            st.write(context)
            st.info("Add an HF text-generation integration or copy context to another LLM.")
        else:
            st.info("Provider/answer path not configured or chat model missing.")

    return
