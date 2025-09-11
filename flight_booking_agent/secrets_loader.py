"""
Secret loading utilities.

Looks for: <project_root>/.streamlit/secrets.toml
Expected structure:
[openai]
api_key = "sk-..."

Precedence:
1. secrets.toml openai.api_key
2. existing environment variable OPENAI_API_KEY
If a key is found in secrets.toml, it is exported to os.environ["OPENAI_API_KEY"] for
libraries that auto-read from the environment.
"""

from __future__ import annotations
import os
from typing import Dict, Any, Optional

try:
    import toml  # lightweight parser
except ImportError as e:  # pragma: no cover
    raise RuntimeError("toml package not installed. Add toml>=0.10.2 to requirements.") from e


def _project_root() -> str:
    return os.path.abspath(os.path.dirname(__file__))


def load_secrets() -> Dict[str, Any]:
    """
    Load secrets file if present. Returns {} if missing or unreadable.
    """
    path = os.path.join(_project_root(), ".streamlit", "secrets.toml")
    if not os.path.exists(path):
        return {}
    try:
        return toml.load(path)
    except Exception:
        return {}


def resolve_openai_api_key(set_env: bool = True) -> Optional[str]:
    """
    Resolve the OpenAI API key using precedence:
      1. secrets.toml: [openai].api_key
      2. environment: OPENAI_API_KEY
    If set_env True and a key is found, exports to environment.
    Returns the key or None.
    """
    secrets = load_secrets()
    file_key = None
    openai_section = secrets.get("openai")
    if isinstance(openai_section, dict):
        file_key = openai_section.get("api_key")

    env_key = os.environ.get("OPENAI_API_KEY")
    api_key = (file_key or env_key or "").strip() or None

    if api_key and set_env:
        os.environ["OPENAI_API_KEY"] = api_key
    return api_key