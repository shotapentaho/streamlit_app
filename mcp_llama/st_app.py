import streamlit as st
import subprocess
import json
import struct
import uuid

st.set_page_config(layout="wide")
st.title("💬 Local LLaMA Chat (MCP via Subprocess)")

prompt = st.text_area("Enter your question:", height=150)

if st.button("🧠 Run LLaMA"):
    if prompt.strip():
        with st.spinner("Thinking..."):
            try:
                # Launch MCP-compatible subprocess
                proc = subprocess.Popen(
                    ["python", "mcp_llama_server.py"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE
                )

                # Send request using MCP format
                req_id = str(uuid.uuid4())
                request = {
                    "type": "request",
                    "id": req_id,
                    "body": {"text": prompt}
                }

                encoded = json.dumps(request).encode("utf-8")
                proc.stdin.write(struct.pack("<I", len(encoded)))
                proc.stdin.write(encoded)
                proc.stdin.flush()

                resp_len = struct.unpack("<I", proc.stdout.read(4))[0]
                resp = json.loads(proc.stdout.read(resp_len))

                if resp["type"] == "response":
                    st.success("Response from LLaMA:")
                    st.markdown(f"> {resp['body']['text']}")
                else:
                    st.error(f"❌ Error: {resp['body']['error']}")

            except Exception as e:
                st.error(f"Failed to run LLaMA subprocess: {e}")
