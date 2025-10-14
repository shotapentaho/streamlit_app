from pathlib import Path

from utils.deeplinks import (
    build_uber_link,
    build_instacart_link,
    build_doordash_link,
    build_ubereats_link,
)
from agents.orchestrator import ServiceAgent
from ui_theme import apply_theme

st.set_page_config(page_title="Agentic Hub", page_icon="🚕 🛒 🍔 🍕 🍽️ ", layout="wide")
apply_theme()
st.markdown(
    """
<style>
#MainMenu {visibility: hidden;}
</style>
""",
    unsafe_allow_html=True
)

# ---------- Helpers ----------
def find_header_image() -> Optional[str]:
    for p in ("hub.png", "images/hub.png", "assets/hub.png", "static/hub.png"):
        if Path(p).exists():
            return p
    return None

def get_openai_api_key_from_secrets() -> Optional[str]:
    try:
        if "OPENAI_API_KEY" in st.secrets:
            return st.secrets["OPENAI_API_KEY"]
        if "openai" in st.secrets and "api_key" in st.secrets["openai"]:
            return st.secrets["openai"]["api_key"]
    except Exception:
        pass
    return None

def get_agent_model_from_secrets(default: str = "gpt-4o-mini") -> str:
    try:
        if "AGENT_MODEL" in st.secrets:
            return st.secrets["AGENT_MODEL"]
        if "openai" in st.secrets and "model" in st.secrets["openai"]:
            return st.secrets["openai"]["model"]
    except Exception:
        pass
    return default

# ---------- Page ----------
#st.markdown("## Services Hub")
st.markdown("""
# 🚕 🛒 🍔 🍕 🍽️  **Services Hub** """)
st.caption("Type what you need. The agent will return the single most relevant service (Uber / Instacart / DoorDash / Uber Eats). If ambiguous, it shows all.")

# One row: left image, right agent input (same level)
left, right = st.columns([1, 1.6], vertical_alignment="center")

with left:
    img_path = find_header_image()
    if img_path:
        st.image(img_path, use_container_width=True)
    else:
        st.empty()

with right:
    openai_api_key = get_openai_api_key_from_secrets()
    model = get_agent_model_from_secrets()
    agent = ServiceAgent(api_key=openai_api_key, model=model)

    if not openai_api_key:
        st.info(
            "Tip: Add your OpenAI API key in .streamlit/secrets.toml for better intent parsing.\n\n"
            'Supported formats:\n'
            'OPENAI_API_KEY = "sk-..."\n\n'
            "[openai]\n"
            'api_key = "sk-..."\n'
            'model = "gpt-4o-mini"\n'
        )

    # Simple, top-level agent input (no Manual tab, no sidebar)
    st.markdown("#### Which service you are looking for?")
    user_query = st.text_input("Example: 'Uber from 1 Stockton St to SFO' or 'Uber Eats sushi'", key="agent_query", label_visibility="collapsed")
    go = st.button("Generate link", type="primary")

    if "last_result" not in st.session_state:
        st.session_state.last_result = None
        st.session_state.last_query = ""

    if go and user_query.strip():
        result = agent.build_links(user_query.strip())
        st.session_state.last_result = result
        st.session_state.last_query = user_query.strip()

    # Results area
    if st.session_state.last_result:
        result = st.session_state.last_result
        st.markdown(f"##### Your request (normalized): {result['readable_request']}")
        if len(result["services"]) == 1:
            st.markdown("Here’s your link:")
        else:
            st.markdown("Ambiguous request. Showing best options:")

        # Show each service result as a compact card
        for entry in result["services"]:
            svc = entry["service"]
            url = entry["url"]
            summary = entry["summary"]
            assumptions = entry.get("assumptions", [])

            with st.container(border=True):
                st.markdown(f"**{svc}**")
                st.markdown(summary)
                if assumptions:
                    st.caption("Notes: " + "; ".join(assumptions))

                st.link_button(f"Open {svc}", url, type="primary")
                st.code(url, language="text")

        # Save a compact markdown log (optional)
        md_lines = [f"Request: {result['readable_request']}"]
        for entry in result["services"]:
            md_lines.append(f"- {entry['service']}: {entry['summary']} -> {entry['url']}")
        st.session_state.last_log = "\n".join(md_lines)
