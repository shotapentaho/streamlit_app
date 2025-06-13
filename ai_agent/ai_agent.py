import streamlit as st
import openai
import os
from langgraph.graph import Graph
from langsmith import traceable

# Set LangSmith environment variables
os.environ["LANGCHAIN_API_KEY"] = st.secrets["langsmith"]["api_key"]
os.environ["LANGCHAIN_PROJECT"] = st.secrets["langsmith"]["project_name"]

client = openai.OpenAI(api_key=st.secrets["openai"]["api_key"])


@traceable(name="AI Agent Run")
def ai_node(data):
    user_message = data["message"]
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}],
        )
        return {"response": response.choices[0].message.content}
    except Exception as e:
        return {"response": f"OPENAI ERROR: {str(e)}"}
        #return {"response": f"Error: {str(e)}"}

graph = Graph()
graph.add_node("ai", ai_node)
graph.set_entry_point("ai")
compiled_graph = graph.compile()

st.set_page_config(layout="wide")
st.title("🧠 LangGraph + LangSmith AI Agent")

col1, col2 = st.columns([1,2])

with col1:
    user_input = st.text_input("Ask your AI agent anything:")

with col2:
    if user_input:
        with st.spinner("Thinking..."):
            result = compiled_graph.invoke({"message": user_input})
            ai_response = (
                result["response"]
                if result and isinstance(result, dict) and "response" in result
                else "Sorry, something went wrong."
            )
            st.markdown(f"**AI:** {ai_response}")

    st.info("This demo uses LangGraph for orchestration and LangSmith for experiment tracking.")