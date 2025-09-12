from __future__ import annotations
import re
from typing import Dict, Any, Optional
import httpx
from bs4 import BeautifulSoup

# Try trafilatura for robust extraction; fall back to BeautifulSoup if unavailable
try:
    import trafilatura  # type: ignore
    HAS_TRAFILATURA = True
except Exception:
    HAS_TRAFILATURA = False


LOGIN_GATING_HINTS = [
    "Sign in", "Join now", "Sign in to view", "Login", "log in", "Continue to LinkedIn"
]

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def fetch_and_extract(url: str, timeout: float = 15.0) -> Dict[str, Any]:
    """
    Attempts to fetch a public LinkedIn page and extract readable text.
    - If page appears gated, returns warning and empty text.
    - Uses trafilatura if available; fallback to a simple BeautifulSoup text extraction.
    """
    warnings = []
    if not re.match(r"^https?://", url):
        url = "https://" + url

    try:
        with httpx.Client(timeout=timeout, follow_redirects=True, headers=DEFAULT_HEADERS) as client:
            resp = client.get(url)
        status = resp.status_code
        if status >= 400:
            return {
                "title": None,
                "text": "",
                "warnings": [f"HTTP {status} when fetching URL."],
            }

        html = resp.text or ""
        # Quick gating detection
        lower_html = html.lower()
        if any(hint.lower() in lower_html for hint in LOGIN_GATING_HINTS) and "linkedin" in lower_html:
            warnings.append("Page appears to be gated (requires sign-in). Please paste the visible content instead.")

        soup = BeautifulSoup(html, "html.parser")
        title = _extract_title(soup)

        # Try robust extraction first
        text = ""
        if HAS_TRAFILATURA:
            try:
                text = trafilatura.extract(html, include_comments=False, include_formatting=False) or ""
            except Exception:
                text = ""

        # Fallback: naive soup extraction
        if not text.strip():
            text = _simple_text_from_soup(soup)

        # Basic cleanup
        text = _clean_text(text)

        return {
            "title": title,
            "text": text,
            "warnings": warnings
        }
    except Exception as e:
        return {
            "title": None,
            "text": "",
            "warnings": [f"Error fetching/extracting: {e}"]
        }


def _extract_title(soup: BeautifulSoup) -> Optional[str]:
    # Prefer og:title if present
    og = soup.find("meta", property="og:title")
    if og and og.get("content"):
        return og.get("content").strip()
    if soup.title and soup.title.text:
        return soup.title.text.strip()
    return None


def _simple_text_from_soup(soup: BeautifulSoup) -> str:
    # Prefer main, article; then headings/paragraphs
    main = soup.find("main") or soup.find("article")
    root = main if main else soup
    parts = []
    for tag in root.find_all(["h1", "h2", "h3", "p", "li"], limit=4000):
        txt = tag.get_text(separator=" ", strip=True)
        if txt:
            parts.append(txt)
    return "\n".join(parts)


def _clean_text(text: str) -> str:
    # Remove excessive whitespace and repeated lines
    lines = [re.sub(r"\s+", " ", ln).strip() for ln in text.splitlines()]
    lines = [ln for ln in lines if ln]
    # de-dup consecutive duplicates
    cleaned = []
    prev = None
    for ln in lines:
        if ln != prev:
            cleaned.append(ln)
        prev = ln
    return "\n".join(cleaned)