# Building a Production-Ready “Ask Your PDF” App with LangChain 0.2, Streamlit, OpenAI, and Gemini

Retrieval-Augmented Generation (RAG) is quickly becoming the default pattern for grounded, controllable LLM applications. In this post, we’ll build a professional-grade “Ask Your PDF” app that lets users upload a PDF and chat with it—powered by modern LangChain (0.2.x), Streamlit, and your choice of LLM provider (OpenAI or Google’s Gemini). We’ll cover key design decisions, versioning pitfalls, and production-minded tips so you can ship with confidence.

## What You’ll Build

- A Streamlit app where:
  - Users upload a PDF on the left; a chat UX lives on the right.
  - The question input stays at the top; newest Q/A appears first.
  - Answers are grounded by retrieved chunks from the PDF via a FAISS vector store.
  - You can switch between OpenAI and Gemini for both embeddings and chat.
  - The app displays which provider/model produced each answer.
- A modern LangChain 0.2.x RAG pipeline using:
  - `create_history_aware_retriever` for context-aware question rewriting.
  - `create_stuff_documents_chain` for concise, context-grounded answers.
  - `create_retrieval_chain` to compose the overall flow.
- A robust setup that avoids Pydantic validation errors (e.g., “qa_prompt extra fields not permitted”) by using the new chain APIs instead of legacy `ConversationalRetrievalChain` parameters.

## Demo

Try the live demo at [ask-pdf-chain.cxloop.co](https://ask-pdf-chain.cxloop.co/). Upload a PDF, pick OpenAI or Gemini, and ask questions with answers grounded in retrieved document context.  
The demo mirrors the architecture in this post, including history‑aware question rewriting, FAISS indexing, MMR retrieval, and provider/model stamps under each response.

## Why RAG for PDFs?

- Grounding: Answers are constrained by your document content, reducing hallucinations.
- Freshness & control: Update the index to reflect the latest docs without re-training a model.
- Transparency: You can show the exact chunks used to answer a question.

## Architecture Overview

1. Ingestion and preprocessing
   - Load the uploaded PDF with `PyPDFLoader`.
   - Chunk text with `RecursiveCharacterTextSplitter` (sliders for size and overlap).
2. Embeddings and index
   - Choose embeddings provider (OpenAI or Gemini).
   - Build a FAISS vector store from the chunks.
3. Retrieval
   - Use MMR retrieval for diversity (`k`, `fetch_k`, `lambda_mult`).
4. LLM reasoning
   - History-aware question rewriting (turn follow-ups into standalone questions).
   - “Stuff” chain answers questions given retrieved context.
5. UX
   - Two-column layout; persistent chat history; latest sources shown under the input.
   - Provider/model metadata displayed under each answer.

## Key Libraries and Versions

With the LangChain 0.2 split packages, imports and APIs have changed. A compatible set looks like:

- langchain>=0.2.x
- langchain-community>=0.2.x
- langchain-openai>=0.1.x
- langchain-google-genai>=1.x
- openai>=1.x
- streamlit>=1.36
- faiss-cpu, pypdf, tiktoken, numpy

This setup:
- Uses the new chain builders (`create_history_aware_retriever`, `create_stuff_documents_chain`, `create_retrieval_chain`).
- Avoids passing legacy prompt arguments to `ConversationalRetrievalChain`, which often triggers Pydantic errors in mixed-version environments.

## Handling the “qa_prompt extra fields not permitted” Error

If you’ve used older LangChain examples, you might have tried:

```python
ConversationalRetrievalChain.from_llm(
  llm=llm,
  retriever=retriever,
  qa_prompt=QA_PROMPT,  # ❌ newer versions often reject this
  condense_question_prompt=...,
)
```

In LangChain 0.2.x, prefer:

- `create_history_aware_retriever(llm, retriever, contextualize_q_prompt)`
- `create_stuff_documents_chain(llm, qa_prompt)`
- `create_retrieval_chain(history_aware_retriever, stuff_docs_chain)`

This API is both cleaner and version-stable.

## Core RAG Flow (Modern LangChain)

```python
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# 1) Prompts
contextualize_q_prompt = ChatPromptTemplate.from_messages([
  ("system", "Rewrite the latest user question as a standalone question. Do not answer."),
  MessagesPlaceholder("chat_history"),
  ("human", "{input}"),
])

qa_prompt = ChatPromptTemplate.from_messages([
  ("system", "Use ONLY the provided context to answer concisely. Note uncertainty if needed."),
  ("human", "Context:\n{context}\n\nQuestion: {input}\n\nAnswer:")
])

# 2) Create chains
history_aware = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)
qa_chain = create_stuff_documents_chain(llm, qa_prompt)
rag_chain = create_retrieval_chain(history_aware, qa_chain)

# 3) Invoke with chat history and input
result = rag_chain.invoke({"input": user_question, "chat_history": chat_history_messages})
answer = result["answer"]
docs_used = result["context"]  # retrieved Documents
```

## Provider Flexibility: OpenAI and Gemini

- Chat:
  - OpenAI: `from langchain_openai import ChatOpenAI`
  - Gemini: `from langchain_google_genai import ChatGoogleGenerativeAI`
- Embeddings:
  - OpenAI: `OpenAIEmbeddings(model="text-embedding-3-small" | "text-embedding-3-large" | "text-embedding-ada-002")`
  - Gemini: `GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")`

Switching providers is as simple as using a sidebar selectbox, instantiating the appropriate LLM and embeddings based on the selection, and rebuilding the index when those choices change.

## UX Details That Matter

- Right-aligned Q&A: A two-column layout keeps upload/settings on the left and interactions on the right.
- Input at the top: The question box appears above the Q&A stream for faster iteration.
- Newest-first display: Users see the latest answer first without scrolling.
- Provider/model stamps: Each assistant message includes “Provider: X • Model: Y”, improving observability and user trust.
- RAG context expander: Show the top chunks used for each answer with page/source metadata and a configurable preview length.

## Performance and Quality Tips

- Chunking:
  - Start with 800–1,200 characters, 100–200 overlap. If retrieval misses key facts, try larger chunks or higher overlap.
- Retrieval:
  - Use MMR (`search_type="mmr"`) to avoid redundant chunks.
  - Tune: `k` (final chunks given to the LLM), `fetch_k` (candidate pool size), and `lambda_mult` (diversity vs similarity).
- “I don’t know” answers:
  - Check extraction: scanned PDFs often produce little text—consider OCR (e.g., Tesseract or cloud OCR) before embedding.
  - Inspect RAG debug: view similarity scores and chunk content to validate index quality.
- Cost and latency:
  - Prefer `text-embedding-3-small` for most apps; upgrade to `-3-large` if quality demands it.
  - Gemini “flash” is faster/cheaper; “pro” is more capable.
  - Cache and reuse vector stores to avoid re-embedding identical docs.

## Security, Secrets, and Configuration

- Configure secrets in `.streamlit/secrets.toml`:
  - OpenAI:
    ```
    [openai]
    api_key = "sk-..."
    ```
  - Gemini:
    ```
    [gemini]
    api_key = "AIza..."
    ```
- Never commit API keys.
- Consider server-side session storage for chat history if dealing with sensitive PDFs.
- If deploying in multi-user settings, isolate indices per user/session to prevent data leakage.

## Persisting and Scaling

- Persistence:
  - Persist FAISS indices to disk to reuse across sessions or after restarts.
  - For multi-doc or multi-tenant apps, organize indices by user-id/document-id.
- Alternatives:
  - Use a hosted vector DB (e.g., Pinecone, Weaviate, Qdrant) when you need horizontal scale, hybrid search, or filtering.
- Concurrency:
  - Streamlit supports multiple users; ensure memory usage remains sane (e.g., limit preview sizes, cap `k`).
- Observability:
  - Track model/provider, request/response tokens, latency, and retrieval stats for tuning.

## Common Pitfalls (and How We Avoided Them)

- Pydantic validation errors:
  - Modernized the chain to `create_*` APIs rather than passing `qa_prompt` to `ConversationalRetrievalChain`.
- Dependency conflicts:
  - Align `langchain`, `langchain-*-providers`, and `google-generativeai` via compatible pins.
  - Prefer not pinning `google-generativeai` directly—let `langchain-google-genai` pull a compatible version.
- Mis-parameterization:
  - In new `langchain_openai`, use `ChatOpenAI(model=...)` (not `model_name`).
  - For legacy integrations, `model_name` may still appear in examples; always match your installed version’s docs.

## Conclusion

With modern LangChain 0.2.x chain builders, a Streamlit UI, and a choice of OpenAI or Gemini backends, you can deliver a robust “Ask Your PDF” RAG app that’s maintainable and production-ready. The approach here avoids common versioning and schema pitfalls, offers strong retrieval quality via MMR, and gives your users a familiar chat experience grounded by their own documents.

If you’d like a ready-to-PR version of this app (with provider/model stamps, newest-first chat, MMR controls, and RAG debug), I can open a pull request to your repository. Just share the repo and target branch.