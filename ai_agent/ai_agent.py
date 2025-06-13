import streamlit as st
from langgraph.graph import Graph
from langsmith import TraceSession, trace
import openai

# Access secrets from .streamlit/secrets.toml
OPENAI_API_KEY = st.secrets["openai"]["api_key"]
LANGSMITH_API_KEY = st.secrets["langsmith"]["api_key"]
PROJECT_NAME = st.secrets["langsmith"]["project_name"]

openai.api_key = OPENAI_API_KEY
ts = TraceSession(project_name=PROJECT_NAME, api_key=LANGSMITH_API_KEY)

def ai_node(data):
    user_message = data["message"]
    # Use OpenAI's GPT model for response generation
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_message}],
    )
    return {"response": response['choices'][0]['message']['content']}

# Define LangGraph
graph = Graph()
graph.add_node("ai", ai_node)
graph.set_entry_point("ai")

# Streamlit UI
st.title("🧠 LangGraph + LangSmith AI Agent")

user_input = st.text_input("Ask your AI agent anything:")

if user_input:
    with st.spinner("Thinking..."):
        with trace(ts, name="AI Agent Run") as run:
            result = graph.invoke({"message": user_input})
            ai_response = result["response"]
            run.log_output(ai_response)
        st.markdown(f"**AI:** {ai_response}")

    # Show LangSmith trace link if available
    if run.url:
        st.markdown(f"[View Trace in LangSmith]({run.url})")

st.info("This demo uses LangGraph for orchestration and LangSmith for experiment tracking.")