import streamlit as st
import openai
import faiss
import numpy as np
from PyPDF2 import PdfReader

# Set Streamlit page config to wide mode and catchy title
st.set_page_config(page_title="Ask Your PDF! 🚀 RAG + FAISS Demo", layout="wide")
st.title("Ask Your PDF! 🚀 – Streamlit RAG with FAISS Demo")

# Use Streamlit secrets for API key
openai_api_key = st.secrets["openai"]["api_key"]
client = openai.OpenAI(api_key=openai_api_key)

def chunk_text(text, chunk_size=500, overlap=100):
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def embed_texts(texts):
    # Batch embed texts using OpenAI (via client)
    response = client.embeddings.create(
        input=texts,
        model="text-embedding-ada-002"
    )
    return np.array([d.embedding for d in response.data])

uploaded_file = st.file_uploader("Upload a PDF or TXT", type=["pdf", "txt"])
query = st.text_input("Ask a question about your document:")

if "chunks" not in st.session_state:
    st.session_state.chunks = []
if "embeddings" not in st.session_state:
    st.session_state.embeddings = None
if "index" not in st.session_state:
    st.session_state.index = None

if uploaded_file:
    if uploaded_file.type == "application/pdf":
        reader = PdfReader(uploaded_file)
        text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
    else:
        text = uploaded_file.read().decode("utf-8")

    chunks = chunk_text(text)
    st.session_state.chunks = chunks
    st.write(f"Document split into {len(chunks)} chunks.")

    embeddings = embed_texts(chunks)
    st.session_state.embeddings = embeddings

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    st.session_state.index = index
    st.success("Document indexed and ready for RAG search!")

if query and st.session_state.index is not None:
    q_emb = embed_texts([query])
    D, I = st.session_state.index.search(q_emb, k=3)
    retrieved_chunks = [st.session_state.chunks[i] for i in I[0]]

    # Split results into two columns
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top Matching Chunks")
        for idx, c in enumerate(retrieved_chunks):
            st.markdown(f"**Chunk {idx+1}:**")
            st.write(c[:500])
            st.write("---")

    with col2:
        context = "\n\n".join(retrieved_chunks)
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Answer the user's question using the provided context."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
        ]
        chat_response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # or "gpt-4o" if you have access
            messages=messages,
            max_tokens=256
        )
        st.subheader("RAG Answer")
        st.write(chat_response.choices[0].message.content.strip())
                                                                                                                                                                                                                                                                                                                                                                                                                    
                                                                             