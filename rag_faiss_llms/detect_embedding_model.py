"""
Detection and embedding helpers for OpenAI, Gemini (Generative Language API), and Vertex AI.

Exports:
- GEMINI_API_BASES
- KNOWN_GEMINI_EMBEDDING_CANDIDATES
- KNOWN_VERTEX_EMBEDDING_CANDIDATES
- detect_available_gemini_embedding_models(api_key) -> List[str]
- detect_openai_embedding_models(api_key) -> List[str]
- detect_vertex_embedding_models(sa_info, project, location) -> List[str]
- openai_embed_texts(texts, model_id, api_key) -> np.ndarray | None
- vertex_embed_texts(texts, model_id, sa_info, project, location) -> np.ndarray | None

Notes:
- Vertex functions require google-auth to be installed and a service account JSON dict.
- All network calls use requests.
"""
from typing import Any, Optional, Tuple, List, Dict
import requests
import numpy as np
import json

# Try to import google auth for Vertex; if absent, Vertex functions will fail with a helpful error.
try:
    from google.oauth2 import service_account
    from google.auth.transport.requests import Request as GoogleRequest
    GOOGLE_AUTH_AVAILABLE = True
except Exception:
    service_account = None
    GoogleRequest = None
    GOOGLE_AUTH_AVAILABLE = False

# Gemini API base candidates to try
GEMINI_API_BASES = (
    "https://generativelanguage.googleapis.com/v1beta",
    "https://generativelanguage.googleapis.com/v1",
)

# Known candidates lists
KNOWN_GEMINI_EMBEDDING_CANDIDATES = [
    "gemini-embedding-001",
    "text-multilingual-embedding-002",
]

KNOWN_VERTEX_EMBEDDING_CANDIDATES = [
    "text-embedding-005",
]

# ---------------------------------------------------------------------------
# Generic embedding extraction helper (handles many response shapes)
# ---------------------------------------------------------------------------
def _extract_embedding_from_response(j: Any) -> Optional[List[float]]:
    """
    Try to extract a single embedding vector from a variety of JSON shapes.
    Returns a list of floats or None if no embedding found.
    Handles:
      - {"embedding": {"value": [...]}} or {"embedding": {"values": [...]}}
      - {"embeddings": [[...]]} or {"embeddings": [{"values": [...]}]}
      - {"data": [{"embedding": [...]}]}
      - [{"embedding": [...]}]
      - Vertex style: {"predictions":[ {"embeddings": {"values": [...]}} , ... ]}
    """
    try:
        # Vertex style: predictions[].embeddings.values
        if isinstance(j, dict) and "predictions" in j and isinstance(j["predictions"], list):
            preds = j["predictions"]
            if preds:
                first = preds[0]
                if isinstance(first, dict):
                    emb_block = first.get("embeddings") or first.get("embedding")
                    if isinstance(emb_block, dict):
                        vals = emb_block.get("values") or emb_block.get("value")
                        if isinstance(vals, list) and vals:
                            return list(map(float, vals))
                    if isinstance(first.get("values"), list):
                        return list(map(float, first.get("values")))
        # generic dict forms
        if isinstance(j, dict):
            emb_obj = j.get("embedding")
            if isinstance(emb_obj, dict):
                vals = emb_obj.get("value") or emb_obj.get("values")
                if vals and isinstance(vals, list):
                    return list(map(float, vals))

            if "embeddings" in j and isinstance(j["embeddings"], list) and j["embeddings"]:
                first = j["embeddings"][0]
                if isinstance(first, list):
                    return list(map(float, first))
                if isinstance(first, dict):
                    vals = first.get("values") or first.get("embedding")
                    if vals and isinstance(vals, list):
                        return list(map(float, vals))

            if "data" in j and isinstance(j["data"], list) and j["data"]:
                first = j["data"][0]
                if isinstance(first, dict) and "embedding" in first:
                    emb = first.get("embedding")
                    if isinstance(emb, list):
                        return list(map(float, emb))
                    if isinstance(emb, dict):
                        vals = emb.get("value") or emb.get("values")
                        if vals and isinstance(vals, list):
                            return list(map(float, vals))

        # Sometimes response is list-of-lists / legacy
        if isinstance(j, list) and j and isinstance(j[0], (list, float, int)):
            first = j[0]
            if isinstance(first, list):
                return list(map(float, first))
            return list(map(float, j))
    except Exception:
        return None
    return None

# ---------------------------------------------------------------------------
# Gemini probing helper
# ---------------------------------------------------------------------------
def _probe_gemini_model_for_embedding(api_key: str, model_id: str, timeout: int = 8) -> bool:
    """
    Try common embed endpoints for a given Gemini model ID.
    Returns True if any endpoint returns a valid embedding.
    """
    headers = {"Content-Type": "application/json"}
    test_text = "hello"
    endpoints = [":embedText", ":embed", ":embedContent"]
    for base in GEMINI_API_BASES:
        base_url = f"{base}/models/{model_id}"
        for ep in endpoints:
            url = f"{base_url}{ep}?key={api_key}"
            if ep == ":embedText":
                payload_variants = [{"text": test_text}, {"content": [{"text": test_text}]}]
            else:
                payload_variants = [{"content": {"parts": [{"text": test_text}]}}]

            for payload in payload_variants:
                try:
                    r = requests.post(url, headers=headers, json=payload, timeout=timeout)
                except Exception:
                    continue
                if r.status_code != 200:
                    continue
                try:
                    j = r.json()
                except Exception:
                    continue
                emb = _extract_embedding_from_response(j)
                if emb:
                    return True
    return False

# ---------------------------------------------------------------------------
# Public detection functions
# ---------------------------------------------------------------------------
def detect_available_gemini_embedding_models(api_key: str) -> List[str]:
    """
    Discover Gemini embedding models available to the provided API key/project.
    Strategy:
      1) Try ListModels on GEMINI_API_BASES and pick names that look like embedding models.
      2) Probe KNOWN_GEMINI_EMBEDDING_CANDIDATES for responsive endpoints.
    """
    found: List[str] = []
    headers = {"Content-Type": "application/json"}

    # 1) Try ListModels
    for base in GEMINI_API_BASES:
        url = f"{base}/models?key={api_key}"
        try:
            r = requests.get(url, headers=headers, timeout=8)
        except Exception:
            continue
        if r.status_code != 200:
            continue
        try:
            j = r.json()
        except Exception:
            continue
        for m in j.get("models", []):
            name = (m.get("name") or "").strip()
            dn = (m.get("displayName") or "").strip().lower()
            lname = name.lower()
            if "embed" in lname or "embed" in dn or "textembedding" in lname or "textembedding" in dn:
                if lname.startswith("models/"):
                    mid = name.split("/", 1)[1]
                else:
                    mid = name
                if mid and mid not in found:
                    found.append(mid)

    # 2) Probe known candidates if not already found
    for candidate in KNOWN_GEMINI_EMBEDDING_CANDIDATES:
        if candidate in found:
            continue
        try:
            ok = _probe_gemini_model_for_embedding(api_key, candidate)
        except Exception:
            ok = False
        if ok:
            found.append(candidate)

    return found

def detect_openai_embedding_models(api_key: str) -> List[str]:
    """
    Query OpenAI's /v1/models and return models that appear to be embedding models.
    """
    if not api_key:
        return []
    url = "https://api.openai.com/v1/models"
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        r = requests.get(url, headers=headers, timeout=12)
    except Exception:
        return []
    if r.status_code != 200:
        return []
    try:
        j = r.json()
    except Exception:
        return []
    out: List[str] = []
    for item in j.get("data", []):
        mid = item.get("id", "") or ""
        mid_l = mid.lower()
        if "embed" in mid_l or "embedding" in mid_l or mid_l.startswith("text-embedding"):
            out.append(mid)
    # dedupe while maintaining order
    seen = set()
    res = []
    for m in out:
        if m not in seen:
            seen.add(m)
            res.append(m)
    return res

# ---------------------------------------------------------------------------
# Vertex detection & embedding helpers
# ---------------------------------------------------------------------------
def _get_vertex_access_token_from_service_account(sa_info: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
    """
    Exchange service account JSON dict for an access token using google-auth.
    Returns (token, error_message). If google-auth is not available, returns error string.
    """
    if not GOOGLE_AUTH_AVAILABLE:
        return None, "google-auth not installed (pip install google-auth)."

    try:
        credentials = service_account.Credentials.from_service_account_info(sa_info, scopes=["https://www.googleapis.com/auth/cloud-platform"])
        request = GoogleRequest()
        credentials.refresh(request)
        return credentials.token, None
    except Exception as e:
        return None, f"Failed to obtain access token: {e}"

def _probe_vertex_model_for_embedding(sa_info: Dict[str, Any], project: str, location: str, model_id: str, timeout: int = 12) -> bool:
    """
    Attempt a minimal predict call to Vertex publisher model to check availability.
    """
    token, err = _get_vertex_access_token_from_service_account(sa_info)
    if not token:
        return False

    region = location
    if location.endswith(("-a", "-b", "-c")):
        region = location.rsplit("-", 1)[0]

    url = f"https://{region}-aiplatform.googleapis.com/v1/projects/{project}/locations/{region}/publishers/google/models/{model_id}:predict"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload_variants = [
        {"instances": [{"content": "hello"}]},
        {"instances": ["hello"]},
        {"instances": [{"text": "hello"}]},
    ]
    for payload in payload_variants:
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=timeout)
        except Exception:
            continue
        if r.status_code != 200:
            continue
        try:
            j = r.json()
        except Exception:
            continue
        emb = _extract_embedding_from_response(j)
        if emb:
            return True
    return False

def detect_vertex_embedding_models(sa_info: Dict[str, Any], project: str, location: str) -> List[str]:
    """
    Probe KNOWN_VERTEX_EMBEDDING_CANDIDATES and return those that respond in the given project/location.
    Requires valid service account info.
    """
    found: List[str] = []
    if not sa_info or not project or not location:
        return found
    for candidate in KNOWN_VERTEX_EMBEDDING_CANDIDATES:
        try:
            ok = _probe_vertex_model_for_embedding(sa_info, project, location, candidate)
        except Exception:
            ok = False
        if ok:
            found.append(candidate)
    return found

def vertex_embed_texts(texts: List[str], model_id: str, sa_info: Dict[str, Any], project: str, location: str) -> Optional[np.ndarray]:
    """
    Call Vertex AI predict endpoint and return numpy array (n_texts, dim) dtype float32 or None on error.
    """
    token, err = _get_vertex_access_token_from_service_account(sa_info)
    if not token:
        print(f"Vertex auth error: {err}")
        return None

    region = location
    if location.endswith(("-a", "-b", "-c")):
        region = location.rsplit("-", 1)[0]

    url = f"https://{region}-aiplatform.googleapis.com/v1/projects/{project}/locations/{region}/publishers/google/models/{model_id}:predict"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {"instances": [{"content": t} for t in texts]}
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=60)
    except Exception as e:
        print(f"Vertex network error: {e}")
        return None

    if r.status_code != 200:
        print(f"Vertex HTTP {r.status_code}: {r.text[:500]}")
        return None

    try:
        j = r.json()
    except Exception as e:
        print(f"Vertex non-JSON response: {e}")
        return None

    # If predictions[] present and contain per-instance embeddings, extract them
    results = []
    if isinstance(j, dict) and "predictions" in j and isinstance(j["predictions"], list):
        for pred in j["predictions"]:
            v = None
            if isinstance(pred, dict):
                emb_block = pred.get("embeddings") or pred.get("embedding")
                if isinstance(emb_block, dict):
                    vals = emb_block.get("values") or emb_block.get("value")
                    if isinstance(vals, list) and vals:
                        v = list(map(float, vals))
                elif isinstance(pred.get("values"), list):
                    v = list(map(float, pred.get("values")))
            if v is None:
                v = _extract_embedding_from_response(pred)
            if v:
                results.append(v)

    if results:
        arr = np.array(results, dtype="float32")
        if arr.ndim == 1:
            arr = arr[None, :]
        return arr

    # Fallback: top-level embedding
    top_v = _extract_embedding_from_response(j)
    if top_v:
        arr = np.array(top_v, dtype="float32")
        if len(texts) == 1:
            return arr[None, :]
        # repeat single vector to match inputs
        return np.vstack([arr for _ in texts]).astype("float32")

    return None

# ---------------------------------------------------------------------------
# OpenAI embedding helper
# ---------------------------------------------------------------------------
def openai_embed_texts(texts: List[str], embedding_model: str, api_key: str) -> Optional[np.ndarray]:
    """
    Call OpenAI embeddings endpoint via openai Python client and return numpy array.
    Returns None on error.
    """
    try:
        import openai as _openai
        client = _openai.OpenAI(api_key=api_key)
        resp = client.embeddings.create(input=texts, model=embedding_model)
        arr = np.array([d.embedding for d in resp.data], dtype="float32")
        if arr.ndim == 1:
            arr = arr[None, :]
        return arr
    except Exception as e:
        print(f"OpenAI embedding error: {e}")
        return None
