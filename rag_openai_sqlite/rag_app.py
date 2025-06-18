import streamlit as st
import openai
import sqlite3
import os
import re

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

def is_question(text):
    import re
    question_words = r"^(who|what|when|where|why|how|is|are|do|does|did|can|could|would|should|will|shall|may|might|whose|whom|which)\b"
    text = text.strip().lower()
    return bool(re.match(question_words, text)) and text.endswith("?")

# ---- App Logic ----
create_db()

st.title("Simple RAG App (OpenAI + SQLite) Streamlit")

# Set your OpenAI API key
openai_api_key = st.secrets["openai"]["api_key"]
client = openai.OpenAI(api_key=openai_api_key)

st.header("1. Add Document")
doc_text = st.text_area("Paste your document text here:")



if st.button("Upload Document"):
    if not doc_text.strip():
        st.warning("Please enter some text.")
    elif is_question(doc_text):
        st.warning("Questions are not allowed. Please enter a statement, not a question.")
    else:
        add_document(doc_text.strip())
        st.success("Document added!")

        
st.header("2. Ask a Question")
question = st.text_input("Your question:")
if st.button("Ask"):
    docs = get_all_documents()
    if not docs:
        st.warning("Please upload at least one document before asking a question.")
    elif not question.strip():
        st.warning("Please enter a question.")
    else:
        tokens = set(question.lower().split())
        relevant = []
        for doc_id, content in docs:
            if any(word in content.lower() for word in tokens):
                relevant.append(content)
        context = "\n\n".join(relevant[:2]) if relevant else ""
        if not context:
            st.info("No relevant information found in your documents.")
        else:
            prompt = f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
            with st.spinner("Generating answer..."):
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
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