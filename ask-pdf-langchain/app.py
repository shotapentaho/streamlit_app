import os
import tempfile
import streamlit as st

# Modern LangChain split packages (compatible with your current requirements)
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

# New retrieval-chain APIs (avoid ConversationalRetrievalChain prompt param issues)
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage
from ui_theme import apply_theme

# --- Helper functions for secrets ---
def get_openai_api_key():
    # secrets.toml:
    # [openai]
    # api_key = "sk-..."
    return st.secrets["openai"]["api_key"]


def get_gemini_api_key():
    # secrets.toml:
    # [gemini]
    # api_key = "AIza..."
    return st.secrets["gemini"]["api_key"]


st.set_page_config(page_title="📄 Query PDF using chain i.e Langchain, LLMs", layout="wide")
st.title("📄 Query PDF (LangChain, LLMs + RAG)")
st.info("LangChain + FAISS:RAG, OpenAIEmbeddings, GoogleGenerativeAIEmbeddings, ConversationalRetrievalChain, RecusiveCharacterTextSplitter")
apply_theme()

# =========================
# Sidebar: Settings
# =========================
st.sidebar.header("⚙️ Settings")

provider = st.sidebar.selectbox("Provider", ["OpenAI", "Gemini"], index=0)

if provider == "OpenAI":
    chat_model = st.sidebar.selectbox(
        "OpenAI chat model",
        ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
        index=0,
    )
    embed_model = st.sidebar.selectbox(
        "OpenAI embedding model",
        ["text-embedding-3-small", "text-embedding-3-large", "text-embedding-ada-002"],
        index=0,
    )
else:
    chat_model = st.sidebar.selectbox(
        "Gemini chat model",
        ["models/gemini-2.5-pro", "models/gemini-2.5-flash"],
        index=0,
    )
    embed_model = st.sidebar.selectbox(
        "Gemini embedding model",
        ["models/embedding-001"],
        #["models/text-embedding-004"],# "models/text-embedding-004"],
        index=0,
    )

temperature = st.sidebar.slider("Creativity (temperature)", 0.0, 1.0, 0.2, 0.1)

# Sliders only: chunk size and overlap
chunk_size = st.sidebar.slider("Chunk size (chars)", min_value=500, max_value=4000, value=1200, step=100)
max_overlap = max(0, chunk_size - 50)
default_overlap = min(200, max_overlap)
chunk_overlap = st.sidebar.slider("Chunk overlap (chars)", min_value=0, max_value=max_overlap, value=default_overlap, step=50)

# RAG retrieval controls
top_k = st.sidebar.slider("Top‑K retrieved chunks", min_value=1, max_value=25, value=10, step=1)
fetch_k = st.sidebar.slider("Fetch‑K (MMR pool size)", min_value=max(10, top_k), max_value=max(30, top_k * 3), value=max(20, top_k * 2), step=1)
lambda_mult = st.sidebar.slider("MMR diversity (0=more diverse, 1=more similar)", 0.0, 1.0, 0.5, 0.05)
preview_chars = st.sidebar.slider("Preview characters per chunk", min_value=200, max_value=3000, value=1000, step=100)
show_debug = st.sidebar.checkbox("Show RAG debug (scores, stats)", value=False)

# =========================
# Session state init
# =========================
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None
if "chat_history" not in st.session_state:
    # Store as list of records: {"q": str, "a": str, "meta": {"provider": str, "model": str}}
    # Backward compatible with older tuple entries (q, a)
    st.session_state.chat_history = []
if "tmp_pdf_path" not in st.session_state:
    st.session_state.tmp_pdf_path = None
if "last_file_sig" not in st.session_state:
    st.session_state.last_file_sig = None
if "doc_stats" not in st.session_state:
    st.session_state.doc_stats = {}
if "latest_sources" not in st.session_state:
    st.session_state.latest_sources = []

# =========================
# Prompts (history-aware retriever + QA "stuff" chain)
# =========================
contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "Given a chat history and the latest user question which might reference prior context, rewrite the latest question into a standalone question. Do not answer the question; only rewrite it."),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system",
         "You are a helpful assistant. Use only the provided context to answer the question.\n"
         "- If the context does not explicitly contain the answer, provide the best helpful summary from the most relevant context, and note any uncertainty.\n"
         "- Quote short phrases from the context when useful.\n"
         "- Be concise and avoid speculation outside the context."
         ),
        ("human", "Context:\n{context}\n\nQuestion: {input}\n\nAnswer:")
    ]
)

# =========================
# Helpers
# =========================
def file_signature(u):
    return f"{u.name}-{u.size}" if hasattr(u, "size") else f"{u.name}-{len(u.getbuffer())}"


def cleanup_temp():
    try:
        if st.session_state.tmp_pdf_path and os.path.exists(st.session_state.tmp_pdf_path):
            os.unlink(st.session_state.tmp_pdf_path)
    except Exception:
        pass
    st.session_state.tmp_pdf_path = None


def build_index_from_uploaded(pdf_file):
    """Persist uploaded file, load, chunk, embed, and build FAISS vectorstore."""
    cleanup_temp()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(pdf_file.getbuffer())
        st.session_state.tmp_pdf_path = tmp.name

    # Load + split
    loader = PyPDFLoader(st.session_state.tmp_pdf_path)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    splits = splitter.split_documents(documents)

    # Stats
    total_chars = sum(len(d.page_content or "") for d in splits)
    st.session_state.doc_stats = {"pages": len(documents), "chunks": len(splits), "chars": total_chars}

    # Embeddings (per provider)
    if provider == "OpenAI":
        embeddings = OpenAIEmbeddings(model=embed_model, api_key=get_openai_api_key())
    else:
        embeddings = GoogleGenerativeAIEmbeddings(model=embed_model, google_api_key=get_gemini_api_key())

    # Vector store
    st.session_state.vectorstore = FAISS.from_documents(splits, embeddings)
    # Reset sources
    st.session_state.latest_sources = []


def messages_from_history():
    """Convert stored history records into LangChain BaseMessages for history-aware retriever."""
    msgs = []
    for item in st.session_state.chat_history:
        if isinstance(item, dict):
            q = item.get("q", "")
            a = item.get("a", "")
        else:
            # backward compatibility with (q, a) tuples
            q, a = item
        if q:
            msgs.append(HumanMessage(content=q))
        if a:
            msgs.append(AIMessage(content=a))
    return msgs


def make_llm():
    """Instantiate the current LLM based on provider/model/temperature."""
    if provider == "OpenAI":
        return ChatOpenAI(model=chat_model, temperature=temperature, api_key=get_openai_api_key())
    else:
        return ChatGoogleGenerativeAI(model=chat_model, temperature=temperature, google_api_key=get_gemini_api_key())


def make_rag_chain(llm):
    """Create a history-aware retriever + stuff-docs QA chain + retrieval chain."""
    # Fresh retriever to reflect current k/fetch_k/lambda_mult
    retriever = st.session_state.vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": top_k, "fetch_k": fetch_k, "lambda_mult": lambda_mult},
    )
    history_aware = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)
    qa_chain = create_stuff_documents_chain(llm, qa_prompt)
    return create_retrieval_chain(history_aware, qa_chain)


# =========================
# Two-column layout (Left: Upload/Manage, Right: Q&A with input at top, newest-first)
# =========================
left, right = st.columns([1, 2], vertical_alignment="top")

with left:
    st.subheader("📥 Upload")
    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"], label_visibility="visible")

    # Build (or rebuild) index when the file or critical settings change
    if uploaded_file:
        sig = f"{file_signature(uploaded_file)}|prov:{provider}|cm:{chat_model}|em:{embed_model}|cs:{chunk_size}|co:{chunk_overlap}"
        need_rebuild = (st.session_state.last_file_sig != sig) or (st.session_state.vectorstore is None)
        if need_rebuild:
            with st.spinner("Processing PDF..."):
                build_index_from_uploaded(uploaded_file)
                st.session_state.last_file_sig = sig
            st.success(f"PDF processed with {provider}. You can now ask questions!")

    # Show stats (help detect scanned PDFs)
    if st.session_state.doc_stats:
        pages = st.session_state.doc_stats.get("pages", 0)
        chunks = st.session_state.doc_stats.get("chunks", 0)
        chars = st.session_state.doc_stats.get("chars", 0)
        st.caption(f"Indexed pages: {pages} | chunks: {chunks} | chars: {chars}")
        if chars < 500:
            st.warning("Very little text extracted. If this is a scanned PDF, consider OCR.")

    st.markdown("### ⚙️ Manage")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Reset chat", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.latest_sources = []
            st.rerun()
    with col2:
        if st.button("🧹 Clear index", use_container_width=True):
            st.session_state.vectorstore = None
            st.session_state.last_file_sig = None
            st.session_state.latest_sources = []
            cleanup_temp()
            st.success("Cleared.")

with right:
    st.subheader("💬 Ask Questions")

    if st.session_state.vectorstore is None:
        st.info("Upload a PDF on the left to enable Q&A.")
    else:
        # 1) Input at the top
        with st.form("qa_form", clear_on_submit=True):
            user_question = st.text_area(
                f"Your question about the PDF ({provider})",
                height=80,
                placeholder="Ask here..."
            )
            submit_q = st.form_submit_button("Ask")

        # 2) Handle submission
        if submit_q and user_question.strip():
            llm = make_llm()
            rag_chain = make_rag_chain(llm)

            # Optional debug: similarity search with raw scores before running chain
            if show_debug:
                try:
                    hits = st.session_state.vectorstore.similarity_search_with_score(user_question, k=top_k)
                except Exception:
                    hits = []
                with st.expander("🧪 RAG Debug: Similarity scores and snippets"):
                    for i, (doc, score) in enumerate(hits, start=1):
                        st.markdown(f"**Hit {i} — score: {score:.4f}**")
                        meta = getattr(doc, "metadata", {}) or {}
                        page = meta.get("page", meta.get("source", ""))
                        if page != "":
                            st.caption(f"Source: {page}")
                        st.write((doc.page_content or "")[:preview_chars])
                        st.write("---")

            # Build message history for the history-aware retriever
            msg_history = messages_from_history()
            result = rag_chain.invoke({"input": user_question, "chat_history": msg_history})

            answer = result.get("answer", "")
            sources = result.get("context", [])  # list[Document]

            # Update history with metadata (chronological storage)
            st.session_state.chat_history.append(
                {"q": user_question, "a": answer, "meta": {"provider": provider, "model": chat_model}}
            )
            st.session_state.latest_sources = sources

        # 3) Latest RAG context under the input
        if st.session_state.latest_sources:
            with st.expander("🔎 Latest RAG context (most recent answer)"):
                for i, doc in enumerate(st.session_state.latest_sources[:top_k], start=1):
                    st.markdown(f"**Chunk {i}**")
                    meta = getattr(doc, "metadata", {}) or {}
                    page = meta.get("page", meta.get("source", ""))
                    if page != "":
                        st.caption(f"Source: {page}")
                    st.write((doc.page_content or "")[:preview_chars])
                    st.write("---")

        # 4) Render chat history NEWEST FIRST in UI with provider/model info
        if st.session_state.chat_history:
            for record in reversed(st.session_state.chat_history):
                # Backward compatibility with old tuple entries
                if isinstance(record, dict):
                    q = record.get("q", "")
                    a = record.get("a", "")
                    meta = record.get("meta", {}) or {}
                    prov_used = meta.get("provider", provider)
                    model_used = meta.get("model", chat_model)
                else:
                    q, a = record
                    prov_used = provider
                    model_used = chat_model

                if q:
                    with st.chat_message("user"):
                        st.write(q)
                with st.chat_message("assistant"):
                    st.write(a)
                    st.caption(f"Provider: {prov_used} • Model: {model_used}")
        else:
            st.caption("Tip: Ask a question above after uploading a PDF.")


st.markdown("---")

# --- TESTIMONIAL / FOOTER ---
st.markdown("""
<div style='text-align: center; font-size: 0.9rem; margin-top: 2rem;'>
    <br><br>
    © 2025 CX Data & Analytics LLC
</div>
""", unsafe_allow_html=True)


st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
