import streamlit as st
import duckdb
from langchain.llms import OpenAI
from langchain.agents import Tool, initialize_agent
from langchain.tools import DuckDuckGoSearchRun

with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    
# Setup DuckDB connection
con = duckdb.connect("agent_memory.duckdb")
con.execute("""
    CREATE TABLE IF NOT EXISTS memory (
        id INTEGER PRIMARY KEY,
        prompt TEXT,
        response TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# Streamlit UI
st.set_page_config(page_title="🤖 DuckDB Agent", layout="centered")
st.title("🧠 AI Agent with DuckDB Memory")

query = st.text_input("Ask me anything:", placeholder="e.g. What's the weather like in Tokyo today?")
show_history = st.checkbox("Show Memory")

# DuckDuckGo Search Tool
search = DuckDuckGoSearchRun()
tools = [Tool(name="WebSearch", func=search.run, description="Search the web")]

# Initialize LLM
llm = OpenAI(api_key=openai_api_key)

# Memory retrieval
if show_history:
    st.subheader("📜 Previous Conversations")
    mem_df = con.execute("SELECT prompt, response, timestamp FROM memory ORDER BY timestamp DESC LIMIT 10").fetchdf()
    st.dataframe(mem_df)

# Main agent logic
if query:
    with st.spinner("Thinking..."):
        agent = initialize_agent(tools, llm, agent="zero-shot-react-description", verbose=True)
        response = agent.run(query)

        # Display
        st.subheader("🤖 Response")
        st.write(response)

        # Store in DuckDB
        con.execute("INSERT INTO memory (prompt, response) VALUES (?, ?)", (query, response))
