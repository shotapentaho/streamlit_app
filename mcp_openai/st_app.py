hide_default_header = """
        <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """
hide_default_footer = """
    <style>
    footer, .st-emotion-cache-1gulkj5 {display: none; visibility: hidden;}
    .css-qri22k {display: none; visibility: hidden;}
    .stDeployButton {display: none;}
    .viewerBadge_link__1S137 {display: none;}
    </style>
"""
hide_github_icon = """
    <style>
        .viewerBadge_container__1QSob,
        .viewerBadge_link__1S137,
        .viewerBadge_text__1JaDK,
        #MainMenu,
        footer {
            display: none !important;
        }
    </style> 
"""

import streamlit as st
st.set_page_config(page_title="MCP Client by CXDA", page_icon="🧠", layout="wide")
st.markdown(hide_default_footer, unsafe_allow_html=True)
st.markdown(hide_default_header, unsafe_allow_html=True)
st.markdown(hide_github_icon, unsafe_allow_html=True)
import requests

st.title("MCP Server Chat Client (OpenAI & Gemini)")
st.markdown("""
Interact with your MCP Server using OpenAI or Gemini models.
Select the provider and pick from available models for your request.
""")

mcp_url = st.text_input("MCP Server URL", value="http://MCP_SERVER_IP:5000/mcp")

# Define available models for each provider
openai_models = [
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-16k",
    "gpt-4",
    "gpt-4-turbo",
    "gpt-4o"
]
gemini_models = [
    "gemini-2.0-flash"
]


provider = st.selectbox("Provider", ["openai", "gemini"])

if provider == "openai":
    model = st.selectbox("OpenAI Model", openai_models)
else:
    model = st.selectbox("Gemini Model", gemini_models)

prompt = st.text_area("Your prompt", height=150)

if st.button("Send"):
    if not prompt.strip():
        st.warning("Please enter a prompt.")
    else:
        with st.spinner("Waiting for response..."):
            try:
                resp = requests.post(
                    mcp_url,
                    json={
                        "provider": provider,
                        "model": model,
                        "prompt": prompt
                    }
                )
                if resp.status_code == 200:
                    st.success("Response received!")
                    st.markdown("**Model Response:**")
                    st.write(resp.json().get("response", "No response field in JSON."))
                else:
                    st.error(f"Error from MCP Server: {resp.text}")
            except Exception as e:
                st.error(f"Request failed: {e}")
