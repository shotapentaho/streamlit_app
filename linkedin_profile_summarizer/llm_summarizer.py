from __future__ import annotations
import os
import json
from typing import Optional, Tuple
import httpx

# If OPENAI_API_KEY is not set, we fall back to a heuristic summarizer.
OPENAI_CHAT_URL = "https://api.openai.com/v1/chat/completions"
DEFAULT_MODEL = "gpt-4o-mini"

SYS_PROMPT = (
    "You are a precise summarizer for professional pages (e.g., LinkedIn). "
    "Your output must be helpful, accurate, and avoid hallucination. "
    "Never invent details that are not present in the provided text. "
    "If certain sections are missing, explicitly state that they were not found."
)

def _truncate(text: str, max_chars: int = 12000) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n...[truncated]"

def _build_user_prompt(text: str, source_url: Optional[str], focus: Optional[str], length_pref: str, include_bullets: bool) -> str:
    parts = []
    if source_url:
        parts.append(f"Source URL: {source_url}")
    if focus:
        parts.append(f"Focus: {focus}")
    parts.append(f"Length preference: {length_pref}")
    parts.append(f"Include bullets: {include_bullets}")
    parts.append("\n=== Content Start ===\n")
    parts.append(text)
    parts.append("\n=== Content End ===\n")

    parts.append(
        "\nPlease produce a concise markdown summary with these sections:\n"
        "1) Overview\n"
        "2) Key Facts (role, company, location, dates) — only if present\n"
        "3) Skills & Topics (from text; do not guess)\n"
        "4) Highlights / Achievements (from text; do not guess)\n"
        "5) Recent Activity (if the content includes posts or articles)\n"
        "6) Notable Quotes (verbatim short quotes if present)\n"
        "7) Actionable Next Steps (what a recruiter/sales/partner might do)\n"
        "Add a 'Missing Data' note for sections that were not found. "
        "Do not include any content that is not grounded in the provided text."
    )
    return "\n".join(parts)

def _heuristic_summary(text: str, length_pref: str, include_bullets: bool) -> str:
    # Extremely simple heuristic fallback: first N sentences + bullets from top lines
    lines = [ln for ln in text.splitlines() if ln.strip()]
    head = " ".join(lines[:5])  # rough overview
    bullets = lines[5:12]  # a few additional points
    bullet_md = ""
    if include_bullets and bullets:
        bullet_md = "\n\n- " + "\n- ".join(bullets[:8])

    size_note = {"short": 2, "medium": 3, "detailed": 4}.get(length_pref, 3)
    overview = " ".join(head.split(". ")[:size_note])

    md = f"### Overview\n{overview}\n"
    if include_bullets and bullet_md:
        md += f"\n### Key Points\n{bullet_md}\n"
    md += "\n### Missing Data\n- This is a heuristic summary (no LLM). Sections may be incomplete."
    return md

def generate_summary(
    text: str,
    source_url: Optional[str] = None,
    focus: Optional[str] = None,
    length_pref: str = "medium",
    include_bullets: bool = True,
    model: str = DEFAULT_MODEL
) -> Tuple[str, bool]:
    """
    Returns (markdown_summary, used_llm)
    """
    text = _truncate(text or "")
    if not text.strip():
        return ("No content provided to summarize.", False)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return (_heuristic_summary(text, length_pref, include_bullets), False)

    user_prompt = _build_user_prompt(text, source_url, focus, length_pref, include_bullets)

    try:
        with httpx.Client(timeout=45.0) as client:
            resp = client.post(
                OPENAI_CHAT_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "temperature": 0.2,
                    "messages": [
                        {"role": "system", "content": SYS_PROMPT},
                        {"role": "user", "content": user_prompt}
                    ]
                }
            )
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        return (content, True)
    except Exception as e:
        fallback = _heuristic_summary(text, length_pref, include_bullets)
        fallback += f"\n\n> Note: LLM call failed, falling back to heuristic. Error: {e}"
        return (fallback, False)