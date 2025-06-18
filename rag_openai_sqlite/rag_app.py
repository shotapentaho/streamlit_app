import streamlit as st
import openai
import sqlite3
import os
import re

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

def drop_table(db_path, table_name):
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        conn.commit()
        print(f"Table '{table_name}' dropped (if it existed).")
    finally:
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
    question_words = r"^(who|what|when|where|why|how|is|are|do|does|did|can|could|would|should|will|shall|may|might|whose|whom|which)\b"
    text = text.strip().lower()
    return text.endswith("?") or bool(re.match(question_words, text))

create_db()

st.title("Simple RAG App (OpenAI + SQLite) Streamlit")

openai_api_key = st.secrets["openai"]["api_key"]
client = openai.OpenAI(api_key=openai_api_key)

st.header("1. Add Document")
doc_text = st.text_area("Paste your document text here:")

if st.button("Upload Document"):
    if not doc_text.strip():
        st.warning("Please enter some text.")
    elif is_question(doc_text):
        st.warning("Questions are not allowed. Please enter a statement, not a question.")
        st.stop()
    else:
        add_document(doc_text.strip())
        st.success("Document added!")

st.header("2. Ask a Question")
question = st.text_input("Your question:")

def find_answer_in_docs(question, docs):
    """
    Try to find an exact match for the question in Q&A docs in the DB.
    Returns the answer if found, else None.
    """
    q_str = question.strip().lower()
    for doc_id, content in docs:
        # Look for Q: ...\nA: ... style
        match = re.search(r"^q:\s*(.*)$\s*a:\s*(.+)", content, re.IGNORECASE | re.MULTILINE | re.DOTALL)
        if match:
            q_in_db = match.group(1).strip().lower()
            a_in_db = match.group(2).strip()
            if q_in_db == q_str:
                return a_in_db
    return None

if st.button("Ask"):
    docs = get_all_documents()
    if not docs:
        st.warning("Please upload at least one document before asking a question.")
    elif not question.strip():
        st.warning("Please enter a question.")
    else:
        # 1. Search for Q&A in DB
        answer = find_answer_in_docs(question, docs)
        if answer:
            st.markdown("**Answer (from DocDB):**")
            st.write(answer)
        else:
            # 2. Not found: ask OpenAI, save to DB as Q&A
            prompt = f"Question: {question}\nAnswer:"
            with st.spinner("No answer found in DocDB. Asking OpenAI..."):
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
            qa_doc = f"Q: {question}\nA: {answer}"
            add_document(qa_doc)
            st.markdown("**Answer (from OpenAI, now saved in DocDB):**")
            st.write(answer)
            st.info("This answer has been saved to your document database for future use.")

st.header("3. Documents in DB")
for doc_id, content in get_all_documents():
    st.markdown(f"- *Doc {doc_id}:* {content[:100]}{'...' if len(content)>100 else ''}")