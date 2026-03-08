"""
Chunking utilities for the RAG app.

This module centralizes text chunking and PDF text extraction so other modules
(importing chunk_text and robust_pdf_text) do not duplicate logic.

Contents:
- chunk_text(text, size, overlap, encoding_name="cl100k_base") -> List[str]
- robust_pdf_text(file) -> str
"""
from typing import List
import tiktoken
from pypdf import PdfReader


def chunk_text(text: str, size: int, overlap: int, encoding_name: str = "cl100k_base") -> List[str]:
    """
    Token-based chunking.

    Parameters:
    - text: input string to chunk
    - size: number of tokens per chunk
    - overlap: number of tokens to overlap between chunks
    - encoding_name: tiktoken encoding name (default "cl100k_base")

    Returns:
    - list of text chunks (strings)
    """
    enc = tiktoken.get_encoding(encoding_name)
    toks = enc.encode(text or "")
    n = len(toks)
    out: List[str] = []
    start = 0
    while start < n:
        end = min(start + size, n)
        piece = toks[start:end]
        if piece:
            out.append(enc.decode(piece))
        # guard against infinite loops if size <= overlap
        advance = max(1, size - overlap)
        start += advance
    return out


def robust_pdf_text(file) -> str:
    """
    Extract text from a PDF file-like object using pypdf.PdfReader.

    Returns concatenated text from all pages. If extraction fails for a page,
    that page is skipped.
    """
    rdr = PdfReader(file)
    parts: List[str] = []
    for p in rdr.pages:
        try:
            txt = p.extract_text() or ""
        except Exception:
            txt = ""
        if txt:
            parts.append(txt)
    return "\n".join(parts)
