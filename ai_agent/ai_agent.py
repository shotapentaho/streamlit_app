import streamlit as st
import openai
import os
from langgraph.graph import Graph
from langsmith import traceable

# Set LangSmith environment variables
os.environ["LANGCHAIN_API_KEY"] = st.secrets["langsmith"]["api_key"]
os.environ["LANGCHAIN_PROJECT"] = st.secrets["langsmith"]["project_name"]

# Set OpenAI API key
openai.api_key = st.secrets["openai"]["api_key"]

@traceable(name="AI Agent Run")
def ai_node(data):
    user_message = data["message"]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_message}],
    )
    return {"response": response["choices"][0]["message"]["content"]}

# Set up LangGraph
graph = Graph()
graph.add_node("ai", ai_node)
graph.set_entry_point("ai")

# Compile the graph
compiled_graph = graph.compile()

st.title("🧠 LangGraph + LangSmith AI Agent")

user_input = st.text_input("Ask your AI agent anything:")

if user_input:
    with st.spinner("Thinking..."):
        result = compiled_graph.invoke({"message": user_input})
        ai_response = result["response"]
        st.markdown(f"**AI:** {ai_response}")

st.info("This demo uses LangGraph for orchestration and LangSmith for experiment tracking.")