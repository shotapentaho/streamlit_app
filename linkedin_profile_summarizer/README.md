# LinkedIn Summarizer (Streamlit)

This Streamlit page summarizes a given (public) LinkedIn page or any pasted content. It uses OpenAI (if a key is present) and falls back to a heuristic summarizer otherwise.

## Features
- Fetch and extract text from public LinkedIn URLs (best effort).
- Respect for LinkedIn Terms: if a page is gated (requires sign-in), the app will not scrape; paste visible text instead.
- OpenAI-powered markdown summary with sections: Overview, Key Facts, Skills, Highlights, Recent Activity, Quotes, Next Steps, Missing Data.
- Heuristic summarization fallback when no API key or LLM errors occur.
- Options for focus prompts, length preference, and bullet points.

## Setup

1) Python deps
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2) Add your OpenAI key (optional, for LLM summaries)
Create `.streamlit/secrets.toml` at the project root:
```toml
[openai]
api_key = "sk-YOUR_KEY"
```
Or export `OPENAI_API_KEY` in your shell.

3) Run
```bash
streamlit run app_linkedin_summary.py
```

## Notes on LinkedIn Content
- Many LinkedIn pages require authentication. This app won't bypass authentication.
- For best results, copy the relevant visible text and paste it directly into the app when access is gated.

## Troubleshooting
- Empty summary: The page might be gated; paste the content instead.
- LLM call failed: Check your network and OpenAI API key/quota. The app will fall back to a heuristic summary.
- Extraction issues: Some pages use heavy client-side rendering; try pasting the content or share links to articles that are publicly available.
