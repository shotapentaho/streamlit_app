import streamlit as st
import openai
import sqlite3
import os

# ---- Database Functions ----
def create_db(db_path="rag_docs.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

def add_document(content, db_path="rag_docs.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('INSERT INTO documents (content) VALUES (?)', (content,))
    conn.commit()
    conn.close()

def get_all_documents(db_path="rag_docs.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT id, content FROM documents')
    docs = c.fetchall()
    conn.close()
    return docs

# ---- App Logic ----
create_db()

st.title("🦾 Simple RAG App (OpenAI + SQLite + Streamlit)")

# Set your OpenAI API key
openai.api_key = st.secrets["openai"]["api_key"]

st.header("1. Add Document")
doc_text = st.text_area("Paste your document text here:")
if st.button("Upload Document"):
    if doc_text.strip():
        add_document(doc_text.strip())
        st.success("Document added!")
    else:
        st.warning("Please enter some text.")

st.header("2. Ask a Question")
question = st.text_input("Your question:")
if st.button("Ask"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        # Retrieve docs, chunk and rank simple way (here: naive keyword matching, improve with embeddings in production)
        docs = get_all_documents()
        # For demo: Find docs containing at least one word from question
        tokens = set(question.lower().split())
        relevant = []
        for doc_id, content in docs:
            if any(word in content.lower() for word in tokens):
                relevant.append(content)
        # Use up to 2 relevant docs, or fall back to all if none match
        context = "\n\n".join(relevant[:2]) if relevant else "\n\n".join([d[1] for d in docs][:2])

        

        prompt = f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
        with st.spinner("Generating answer..."):
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.2,
            )
            answer = response.choices[0].message.content.strip()

        st.markdown("**Answer:**")
        st.write(answer)

st.header("3. Documents in DB")
for doc_id, content in get_all_documents():
    st.markdown(f"- *Doc {doc_id}:* {content[:100]}{'...' if len(content)>100 else ''}")