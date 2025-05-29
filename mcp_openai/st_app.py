import streamlit as st
import requests

st.set_page_config(layout="wide")
st.title("🧠 MCP Client")

model = st.selectbox("Choose a model", ["gpt-3.5-turbo", "gpt-4"])
prompt = st.text_area("Enter your prompt:")

if st.button("Send to MCP Server at MCP_SERVER_IP:5000 "):
    if not prompt.strip():
        st.warning("Please enter a prompt before sending.")
    else:
        with st.spinner("Waiting for response..."):
            try:
                url = "http://[MCP_SERVER_IP]:5000/mcp"
                response = requests.post(url, json={"prompt": prompt, "model": model})
                st.write("Response status code:", response.status_code)

                if response.status_code == 200:
                    data = response.json()
                    st.success("Response from model:")
                    st.write(data["response"])
                else:
                    st.error(f"Server error: {response.text}")
            except Exception as e:
                st.error(f"Connection failed: {e}")
