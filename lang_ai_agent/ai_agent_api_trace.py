import os
import streamlit as st
import requests
from langgraph.graph import Graph
from langsmith import traceable
import openai

st.set_page_config(layout="wide")

# Set environment variables from secrets
os.environ["LANGCHAIN_API_KEY"] = st.secrets["langsmith"]["api_key"]
os.environ["LANGCHAIN_PROJECT"] = st.secrets["langsmith"]["project_name"]

#st.write("Project:", os.environ.get("LANGCHAIN_PROJECT"))
client = openai.OpenAI(api_key=st.secrets["openai"]["api_key"])
api_key = st.secrets["OPEN_WEATHER"]["OPENWEATHER_API_KEY"]  # Add your key to .streamlit/secrets.toml
cities = [
    "New York",
    "London",
    "Tokyo",
    "Sydney",
    "Cape Town",
    "São Paulo"
]

cols = st.columns(len(cities))

for idx, city in enumerate(cities):
    with cols[idx]:
        url = (
            f"https://api.openweathermap.org/data/2.5/weather?q={city}"
            f"&appid={api_key}&units=metric"
        )
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            icon_code = data['weather'][0]['icon']
            icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
            st.image(icon_url, width=60)
            st.markdown(
                f"**{city}**<br>"
                f"{data['main']['temp']}°C<br>"
                f"{data['weather'][0]['description'].title()}",
                unsafe_allow_html=True
            )
        else:
            st.error("API error")

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

        # --- API Endpoint + Payload display and send ---
        st.subheader("Send Trace via LangSmith API")
        api_url = "https://api.smith.langchain.com/runs"
        api_key = st.secrets["langsmith"]["api_key"]
        project_name = st.secrets["langsmith"]["project_name"]
        payload = {
            "name": "Streamlit Manual Trace",
            "project_name": project_name,
            "run_type": "chain",
            "inputs": {"input": user_input, "model": model_name},
            "outputs": {"output": ai_response},
            "extra": {},
            "tags": ["api_test", "streamlit"]
        }
        st.code(f"""POST {api_url}
Headers:
    x-api-key: {api_key}
    Content-Type: application/json
Payload:
{payload}
""", language="python")

        if st.button("Send Trace via API"):
            headers = {
                "x-api-key": api_key,
                "Content-Type": "application/json"
            }
            response = requests.post(api_url, headers=headers, json=payload)
            st.write("API response:", response.status_code, response.text)

            if response.status_code in [200, 201, 202]:
                st.success("Trace successfully sent via API! Check your LangSmith dashboard.")
            else:
                st.error(f"Error sending trace via API. Status: {response.status_code} Body: {response.text}")
    st.info("This demo uses LangGraph for orchestration and LangSmith for experiment tracking.")