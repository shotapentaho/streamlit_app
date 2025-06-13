import os
import streamlit as st
st.set_page_config(layout="wide")


os.environ["LANGCHAIN_API_KEY"] = st.secrets["langsmith"]["api_key"]
os.environ["LANGCHAIN_PROJECT"] = st.secrets["langsmith"]["project_name"]

from langgraph.graph import Graph
from langsmith import traceable
import openai

@traceable
def add(a, b):
    return a + b

if st.button("Test Trace"):
    result = add(1, 2)
    st.write("Result:", result)

st.write("Project:", os.environ.get("LANGCHAIN_PROJECT"))
client = openai.OpenAI(api_key=st.secrets["openai"]["api_key"])

@traceable(name="AI Agent Run")
def ai_node(data):
    try:
        user_message = data["message"]
        model = data.get("model", "gpt-3.5-turbo")
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": user_message}],
        )
        return {"response": response.choices[0].message.content}
    except Exception as e:
        return {"response": f"OPENAI ERROR: {str(e)}"}

graph = Graph()
graph.add_node("ai", ai_node)
graph.set_entry_point("ai")
graph.set_finish_point("ai")
compiled_graph = graph.compile()


st.title("🧠 LangGraph + LangSmith AI Agent")

col1, col2 = st.columns([1,2])

with col1:
    user_input = st.text_input("Ask your AI agent anything:")
    model_name = st.selectbox(
        "Choose OpenAI model:",
        ["gpt-3.5-turbo", "gpt-4o", "gpt-4-turbo", "gpt-4"],
        index=0
    )

with col2:
    if user_input:
        with st.spinner("Thinking..."):
            result = compiled_graph.invoke({"message": user_input, "model": model_name})
            st.write("Raw result:", result)
            ai_response = (
                result["response"]
                if result and isinstance(result, dict) and "response" in result
                else "Sorry, something went wrong."
            )
            st.markdown(f"**AI:** {ai_response}")

    st.info("This demo uses LangGraph for orchestration and LangSmith for experiment tracking.")