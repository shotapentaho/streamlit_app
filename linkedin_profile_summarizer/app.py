import streamlit as st
from typing import Optional
from linkedin_fetcher import fetch_and_extract
from llm_summarizer import generate_summary
from secrets_loader import resolve_openai_api_key

st.set_page_config(page_title="LinkedIn Page Summarizer", page_icon="🔎", layout="wide")
st.title("🔎 LinkedIn Page Summarizer")

# Resolve OpenAI API key (secrets.toml > env var)
api_key = resolve_openai_api_key(set_env=True)
if api_key:
    st.sidebar.success("OpenAI key loaded from secrets/env.")
else:
    st.sidebar.warning("No OpenAI key found. Will use heuristic (non-LLM) summarization.")

st.sidebar.markdown("—")
st.sidebar.caption("Please respect LinkedIn's Terms of Service.")

with st.expander("How this works"):
    st.markdown(
        "- If a LinkedIn page is publicly accessible, we attempt to extract the visible text and summarize it.\n"
        "- If the page is gated (requires sign-in), we will not scrape it; please paste the content you can see.\n"
        "- You can also paste any content (e.g., copied profile sections, posts, or exported text)."
    )

st.subheader("1) Provide Content")
url = st.text_input("LinkedIn URL (publicly accessible)", placeholder="https://www.linkedin.com/in/... or /posts/... or /pulse/...")
pasted_text = st.text_area("Or paste content directly (preferred for gated pages)", height=200, placeholder="Paste text content here...")

st.subheader("2) Options")
focus = st.text_input(
    "Optional: Focus areas (e.g., 'summarize recent posts and key skills', 'highlight B2B growth metrics')",
    value=""
)
length_pref = st.selectbox(
    "Summary length",
    options=["short", "medium", "detailed"],
    index=1
)
include_bullets = st.checkbox("Include concise bullet points", value=True)

st.subheader("3) Generate Summary")
if st.button("Summarize"):
    content_text: Optional[str] = None
    title: Optional[str] = None
    warnings = []

    if pasted_text.strip():
        content_text = pasted_text.strip()
        title = "Pasted Content"
    elif url.strip():
        with st.spinner("Fetching page content..."):
            result = fetch_and_extract(url.strip())
        title = result.get("title") or "LinkedIn Page"
        warnings = result.get("warnings", [])
        content_text = result.get("text")
        if not content_text or len(content_text.strip()) == 0:
            st.error("No readable content extracted. If the page is gated, please paste the content manually.")
            if warnings:
                with st.expander("Warnings"):
                    for w in warnings:
                        st.warning(w)
            st.stop()
    else:
        st.error("Please provide a LinkedIn URL (public) or paste content.")
        st.stop()

    with st.spinner("Summarizing..."):
        summary_md, used_llm = generate_summary(
            text=content_text,
            source_url=url.strip() or None,
            focus=focus.strip() or None,
            length_pref=length_pref,
            include_bullets=include_bullets
        )

    st.success(f"Summary ready ({'LLM' if used_llm else 'Heuristic'}).")
    st.markdown(f"### Summary: {title}")
    st.markdown(summary_md)

    with st.expander("Preview Extracted Content"):
        st.text(content_text[:15000] + ("\n... [truncated]" if len(content_text) > 15000 else ""))

    if warnings:
        with st.expander("Warnings"):
            for w in warnings:
                st.warning(w)

st.markdown("---")
st.caption("Tip: For gated pages, copy visible sections (About, Experience, Post text) and paste them above for the best results.")