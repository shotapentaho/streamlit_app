import streamlit as st
import openai
import faiss
import numpy as np
from pypdf import PdfReader
import requests
from ui_theme import apply_theme
import tiktoken


# --- Streamlit page setup ---
st.set_page_config(page_title="Ask PDF! 🚀 RAG with FAISS", layout="wide")
apply_theme()

hide_menu_style = """
    <style>
    #MainMenu {visibility: hidden;}
    </style>
    """
st.markdown(hide_menu_style, unsafe_allow_html=True)

# --- API keys ---
openai_api_key = st.secrets["openai"]["api_key"]
gemini_api_key = st.secrets["gemini"]["api_key"]
huggingface_api_token = st.secrets["huggingface"]["api_token"]

# --- HuggingFace Embedding Models ---
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
        "gemini-embedding-001":"gemini-embedding-001"
        #"embedding-001": "embedding-001"
    },
    "HuggingFace": HF_MODELS
}
OPENAI_CHAT_MODELS = [
    "gpt-4",
    "gpt-4-turbo",
    "gpt-3.5-turbo"
]
#GEMINI_CHAT_MODEL = "gemini-1.5-pro-latest"  #Oct3
GEMINI_CHAT_MODEL = "gemini-2.5-pro"


# --- Session state initialization ---
if "chunks" not in st.session_state:
    st.session_state.chunks = []
if "model_embeddings" not in st.session_state:
    st.session_state.model_embeddings = {}  # {(provider,model): np.ndarray}
if "model_indexes" not in st.session_state:
    st.session_state.model_indexes = {}     # {(provider,model): faiss.Index}
if "pdf_loaded" not in st.session_state:
    st.session_state.pdf_loaded = False
if "last_file_name" not in st.session_state:
    st.session_state.last_file_name = None


st.title("Ask PDF, query for semantic results 🚀 ")
st.subheader("Powered by: LLMs (OpenAI, Gemini, HuggingFace embedding/chat) + RAG (FAISS)")

# --- UI: File Upload and LLM/Embedding Model Picker in 2 columns ---
col1, col2, col3 = st.columns(3)
with col1:
    uploaded_file = st.file_uploader("Browse: Upload a PDF or TXT", type=["pdf", "txt"])
with col2:
    provider = st.selectbox("LLM Providers:", list(EMBED_MODELS.keys()))
with col3:
    model = st.selectbox(
        "Text embedding model:",
        list(EMBED_MODELS[provider].keys()),
        key=f"model_select_{provider}"
    )

if provider == "OpenAI":
    openai_chat_model = st.selectbox(
        "OpenAI chat model:",
        OPENAI_CHAT_MODELS,
        key="openai_chat_model"
    )
    gemini_chat_model = None
elif provider == "Gemini":
    openai_chat_model = None
    gemini_chat_model = GEMINI_CHAT_MODEL
else:
    openai_chat_model = None
    gemini_chat_model = None

# Embedding parameters
with st.sidebar:
    st.header("Embedding & Generation Parameters")
    temperature = st.slider("Temperature", 0.0, 2.0, 0.6, 0.01)
    max_tokens = st.slider("Max tokens", 32, 2048, 256, 8)
    top_p = st.slider("Top P", 0.0, 1.0, 1.0, 0.01)
    frequency_penalty = st.slider("Frequency Penalty", 0.0, 2.0, 0.0, 0.01)
    presence_penalty = st.slider("Presence Penalty", 0.0, 2.0, 0.0, 0.01)

# If a new file is uploaded, reset all caches
if uploaded_file is not None:
    file_id = uploaded_file.name + str(uploaded_file.size)
    if file_id != st.session_state.last_file_name:
        st.session_state.chunks = []
        st.session_state.model_embeddings = {}
        st.session_state.model_indexes = {}
        st.session_state.pdf_loaded = False
        st.session_state.last_file_name = file_id

def chunk_text(text, chunk_size=500, overlap=100, encoding_name="cl100k_base"):
    encoding = tiktoken.get_encoding(encoding_name)
    tokens = encoding.encode(text)
    chunks = []
    start = 0
    n = len(tokens)

    while start < n:
        end = min(start + chunk_size, n)
        piece = tokens[start:end]
        if piece:
            chunks.append(encoding.decode(piece))
        start += max(1, chunk_size - overlap)

    return chunks


def openai_embed_texts(texts, embedding_model):
    try:
        client = openai.OpenAI(api_key=openai_api_key)
        response = client.embeddings.create(
            input=texts,
            model=embedding_model
        )
        arr = np.array([d.embedding for d in response.data], dtype="float32")
        if len(arr.shape) == 1:
            arr = np.expand_dims(arr, axis=0)
        return arr

    except openai.RateLimitError:
        st.error("⚠️ You have exceeded your OpenAI quota. Please check your plan and billing details.")
        st.info("See [OpenAI Billing Dashboard](https://platform.openai.com/account/billing/overview) for more info.")
        return None

    except openai.OpenAIError as e:
        st.error(f"An OpenAI API error occurred: {str(e)}")
        return None

def gemini_embed_texts(texts, embedding_model):
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{embedding_model}:embedContent?key={gemini_api_key}"
    embeddings = []
    headers = {"Content-Type": "application/json"}
    progress = st.progress(0, text="Gemini: embedding chunks...")
    for i, text in enumerate(texts):
        data = { "content": { "parts": [{ "text": text }] } }
        resp = requests.post(api_url, headers=headers, json=data)
        if resp.status_code != 200:
            st.error(f"Gemini API error: {resp.status_code}: {resp.text}")
            embeddings.append([0.0])
        else:
            out = resp.json()
            emb = out.get("embedding", {}).get("value", [])
            if not emb and "embedding" in out:
                emb = out["embedding"].get("values", [])
            embeddings.append(emb if emb else [0.0])
        progress.progress((i+1)/len(texts))
    progress.empty()
    arr = np.array(embeddings, dtype="float32")
    if len(arr.shape) == 1:
        arr = np.expand_dims(arr, axis=0)
    if len(arr.shape) == 3:
        arr = arr.mean(axis=1)
    return arr

def hf_embed_texts(texts, embedding_model_name, fallback_dim=None):
    api_url = f"https://api-inference.huggingface.co/models/{embedding_model_name}"
    headers = {
        "Authorization": f"Bearer {huggingface_api_token}",
        "Content-Type": "application/json"
    }
    embeddings = []
    for text in texts:
        data = {"inputs": text}
        resp = requests.post(api_url, headers=headers, json=data)
        if resp.status_code != 200:
            pooled = np.zeros(fallback_dim if fallback_dim else 23, dtype="float32")
            embeddings.append(pooled)
        else:
            out = resp.json()
            # If output is [tokens, dim] shape
            if isinstance(out, list) and isinstance(out[0], list):
                arr = np.array(out, dtype="float32")
                pooled = arr.mean(axis=0)
                embeddings.append(pooled)
            elif isinstance(out, list):
                embeddings.append(np.array(out, dtype="float32"))
            else:
                embeddings.append(np.zeros(fallback_dim if fallback_dim else 23, dtype="float32"))
    arr = np.array(embeddings, dtype="float32")
    # Always ensure arr is shape (N, dim) for FAISS
    if len(arr.shape) == 1:
        arr = np.expand_dims(arr, axis=0)
    if len(arr.shape) == 3:
        arr = arr.mean(axis=1)
    return arr

EMBED_FUNCS = {
    "OpenAI": openai_embed_texts,
    "Gemini": gemini_embed_texts,
    # For HuggingFace, we will set fallback_dim at runtime
    "HuggingFace": None
}

if uploaded_file and not st.session_state.pdf_loaded:
    with st.spinner("Reading and splitting document..."):
        if uploaded_file.type == "application/pdf":
            reader = PdfReader(uploaded_file)
            text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
        else:
            text = uploaded_file.read().decode("utf-8", errors="replace")
        chunks = chunk_text(text)
        st.session_state.chunks = chunks
        st.write(f"Document split into {len(chunks)} chunks.")
    st.session_state.pdf_loaded = True

current_key = (provider, model)
if st.session_state.pdf_loaded and st.session_state.chunks:
    if current_key not in st.session_state.model_embeddings:
        with st.spinner(f"Embedding document chunks using {provider} / {model}..."):
            if provider == "HuggingFace":
                # Use first chunk to get embedding dim
                test_emb = hf_embed_texts([st.session_state.chunks[0]], EMBED_MODELS["HuggingFace"][model])
                embedding_dim = test_emb.shape[1]
                embed_func = lambda texts, model_name: hf_embed_texts(texts, model_name, fallback_dim=embedding_dim)
                EMBED_FUNCS["HuggingFace"] = embed_func
            embed_func = EMBED_FUNCS[provider]
            embeddings = embed_func(st.session_state.chunks, EMBED_MODELS[provider][model])
            st.write("Embeddings shape:", embeddings.shape)
            # Ensure correct shape and dtype for FAISS
            if len(embeddings.shape) == 1:
                embeddings = np.expand_dims(embeddings, axis=0)
            if len(embeddings.shape) == 3:
                embeddings = embeddings.mean(axis=1)
            embeddings = embeddings.astype("float32", copy=False)

            index = faiss.IndexFlatL2(embeddings.shape[1])
            index.add(embeddings)
            st.session_state.model_embeddings[current_key] = embeddings
            st.session_state.model_indexes[current_key] = index
        st.success(f"Document indexed for {provider}/{model} and ready for RAG search!")

if (
    st.session_state.pdf_loaded
    and st.session_state.chunks
    and current_key in st.session_state.model_indexes
    and st.session_state.model_indexes[current_key] is not None
):
    st.info(f"Embeddings generated using: {provider} / {model}")
    query = st.text_input("Ask a question about your document:")

    if query:
        # Retrieval controls (dynamic, based on corpus size)
        corpus_size = len(st.session_state.chunks)
        with st.sidebar:
            st.header("Retrieval Parameters")
            top_k = st.slider(
                "Top‑K retrieved chunks",
                min_value=1,
                max_value=max(1, min(100, corpus_size)),
                value=min(10, corpus_size),
                step=1,
                help="Number of chunks to retrieve from FAISS"
            )
            preview_chars = st.slider(
                "Preview characters per chunk",
                min_value=200,
                max_value=4000,
                value=1000,
                step=100,
                help="How much of each chunk to display in the results"
            )

        if provider == "HuggingFace":
            embedding_dim = st.session_state.model_embeddings[current_key].shape[1]
            embed_func = lambda texts, model_name: hf_embed_texts(texts, model_name, fallback_dim=embedding_dim)
        else:
            embed_func = EMBED_FUNCS[provider]

        q_emb = embed_func([query], EMBED_MODELS[provider][model])
        st.write("Query embedding shape:", q_emb.shape)
        # Ensure correct shape for FAISS search
        if len(q_emb.shape) == 1:
            q_emb = np.expand_dims(q_emb, axis=0)
        if len(q_emb.shape) == 3:
            q_emb = q_emb.mean(axis=1)
        q_emb = q_emb.astype("float32", copy=False)

        doc_embeddings = st.session_state.model_embeddings[current_key]
        index_dim = doc_embeddings.shape[1]
        query_dim = q_emb.shape[1]
        if query_dim != index_dim:
            st.error(f"Query embedding dim {query_dim} does not match index dim {index_dim}.")
        else:
            index = st.session_state.model_indexes[current_key]
            D, I = index.search(q_emb, k=min(top_k, corpus_size))

            # Remove invalid/duplicate indices while preserving order
            seen = set()
            retrieved_idxs = []
            for i in I[0]:
                if i == -1 or i in seen:
                    continue
                seen.add(i)
                retrieved_idxs.append(i)

            retrieved_chunks = [st.session_state.chunks[i] for i in retrieved_idxs]

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Top Matching Chunks")
                for idx, c in enumerate(retrieved_chunks, start=1):
                    st.markdown(f"**Chunk {idx}:**")
                    st.write(c[:preview_chars])
                    st.write("---")

            with col2:
                context = "\n\n".join(retrieved_chunks)
                if provider == "OpenAI" and openai_chat_model:
                    try:
                        client = openai.OpenAI(api_key=openai_api_key)
                        messages = [
                            {"role": "system", "content": "You are a helpful assistant. Answer the user's question using the provided context."},
                            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
                        ]
                        chat_response = client.chat.completions.create(
                            model=openai_chat_model,
                            messages=messages,
                            max_tokens=max_tokens,
                            temperature=temperature,
                            top_p=top_p,
                            frequency_penalty=frequency_penalty,
                            presence_penalty=presence_penalty
                        )
                        st.subheader("RAG Answer (OpenAI)")
                        st.write(chat_response.choices[0].message.content.strip())
                    except openai.RateLimitError as e:
                        st.error("⚠️ You have exceeded your OpenAI quota. Please check your plan and billing details.")
                        st.info("See [OpenAI Billing Dashboard](https://platform.openai.com/account/billing/overview) for more info.")
                        #return None
                elif provider == "Gemini" and gemini_chat_model:
                    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{gemini_chat_model}:generateContent?key={gemini_api_key}"
                    #api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{gemini_chat_model}:embedContent?key={gemini_api_key}"
                    headers = {"Content-Type": "application/json"}
                    data = {
                        "contents": [
                            {
                                "parts": [{"text": f"Context:\n{context}\n\nQuestion: {query}"}]
                            }
                        ],
                        "generationConfig": {
                            "temperature": temperature,
                            "maxOutputTokens": max_tokens,
                            "topP": top_p,
                            "frequencyPenalty": frequency_penalty,
                            "presencePenalty": presence_penalty
                        }
                    }
                    with st.spinner("Gemini generating answer..."):
                        resp = requests.post(api_url, headers=headers, json=data)
                    if resp.status_code != 200:
                        st.subheader("RAG Answer (Gemini)")
                        st.error(f"Gemini API error: {resp.status_code}: {resp.text}")
                    else:
                        out = resp.json()
                        candidate = ""
                        try:
                            candidate = out["candidates"][0]["content"]["parts"][0]["text"]
                        except Exception:
                            candidate = str(out)
                        st.subheader("RAG Answer (Gemini)")
                        st.write(candidate)
                elif provider == "HuggingFace":
                    st.subheader(f"RAG Context ({model})")
                    st.write(context)
                    st.info("You can copy-paste above context to an LLM for further Q&A, or add direct integration with Hugging Face Inference endpoints or OpenAI/Gemini.")


st.markdown("---")

# --- TESTIMONIAL / FOOTER ---
st.markdown("""
<div style='text-align: center; font-size: 0.9rem; margin-top: 2rem;'>
    <br><br>
    © 2025 CX Data & Analytics LLC
</div>
""", unsafe_allow_html=True)


st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)


