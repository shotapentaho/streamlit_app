import streamlit as st
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI

# --- Helper function for secrets ---
def get_open_ai_api_key():
    return st.secrets["open_ai"]["api_key"]

# Streamlit app config
st.set_page_config(page_title="Ask your PDF (LangChain)", layout="wide")
st.title("📄 Ask your PDF (LangChain)")

# --- Sidebar settings ---
st.sidebar.header("⚙️ Settings")

model_choice = st.sidebar.selectbox(
    "Choose an LLM model:",
    ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
    index=0
)

temperature = st.sidebar.slider("Creativity (temperature)", 0.0, 1.0, 0.2, 0.1)
chunk_size = st.sidebar.number_input("Chunk size", min_value=500, max_value=2000, value=1000, step=100)
chunk_overlap = st.sidebar.number_input("Chunk overlap", min_value=50, max_value=500, value=200, step=50)

# --- Main UI ---
uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_file:
    with st.spinner("Processing PDF..."):
        # 1. Load PDF
        loader = PyPDFLoader(uploaded_file)
        documents = loader.load()

        # 2. Split into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        splits = text_splitter.split_documents(documents)

        # 3. Create vector store
        embeddings = OpenAIEmbeddings(openai_api_key=get_open_ai_api_key())
        vectorstore = FAISS.from_documents(splits, embeddings)

        # 4. Build retrieval chain
        llm = ChatOpenAI(
            model=model_choice,
            temperature=temperature,
            openai_api_key=get_open_ai_api_key()
        )
        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=vectorstore.as_retriever(),
            return_source_documents=True,
        )

        # 5. Chat UI
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        user_question = st.chat_input("Ask something about the PDF...")
        if user_question:
            result = qa_chain(
                {"question": user_question, "chat_history": st.session_state.chat_history}
            )
            answer = result["answer"]
            sources = result["source_documents"]

            # Update chat history
            st.session_state.chat_history.append((user_question, answer))

            # Display conversation
            with st.chat_message("user"):
                st.write(user_question)
            with st.chat_message("assistant"):
                st.write(answer)

                with st.expander("📑 Sources"):
                    for i, doc in enumerate(sources, 1):
                        st.write(f"Source {i}:")
                        st.write(doc.page_content[:500] + "...") 