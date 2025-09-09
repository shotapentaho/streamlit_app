
import os
import json
import time
import traceback
from typing import List, Optional, Dict, Any

import streamlit as st
import pandas as pd
import plotly.express as px
import toml  # NEW: for reading local secrets.toml

from agent_models import (
    AnalysisPlan,
    FinalAnswer,
    ChartSpec,
    ToolInvocationResult,
    LLMMessage,
)
from agent_tools import (
    DataContext,
    build_profile,
    run_dataframe_query,
    summarize_column,
    detect_anomalies,
    generate_chart_df,
)
from agent_runner import DataAnalystAgent, AgentConfig

# ------------------------------------------------------------------------------------
# Streamlit Page Config
# ------------------------------------------------------------------------------------
st.set_page_config(
    page_title="Data Analyst Agent",
    layout="wide",
    page_icon="📊",
)

st.title("📊 Data Analyst Agent")

# ------------------------------------------------------------------------------------
# ---------------- Secrets / API Key ----------------
# Replaced previous dynamic / session fallback logic with explicit file + env resolution.
# Reads: <repo_root>/.streamlit/secrets.toml relative to this file.
# secrets.toml expected structure:
# [openai]
# api_key = "sk-..."
# Fallback: OPENAI_API_KEY environment variable.
# ------------------------------------------------------------------------------------
def load_secrets() -> Dict[str, Any]:
    base_dir = os.path.dirname(__file__)
    path = os.path.join(base_dir, ".streamlit", "secrets.toml")
    if not os.path.exists(path):
        return {}
    try:
        return toml.load(path)
    except Exception as e:
        st.warning(f"Failed to read secrets.toml: {e}")
        return {}

SECRETS = load_secrets()

def resolve_api_key() -> str:
    file_key = SECRETS.get("openai", {}).get("api_key") if isinstance(SECRETS.get("openai"), dict) else None
    env_key = os.environ.get("OPENAI_API_KEY")
    api_key = (file_key or env_key or "").strip()
    if not api_key:
        st.error("OpenAI API key not found in .streamlit/secrets.toml or OPENAI_API_KEY env var.")
        st.stop()
    os.environ["OPENAI_API_KEY"] = api_key
    return api_key

openai_key = resolve_api_key()

# ------------------------------------------------------------------------------------
# Sidebar: Configuration (reduced – no key input)
# ------------------------------------------------------------------------------------
with st.sidebar:
    st.header("Configuration")
    st.success("OpenAI key loaded (file/env).")
    model_choice = st.selectbox(
        "LLM Model",
        ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini", "gpt-4.1"],
        index=0
    )
    max_rows_preview = st.slider("Preview Rows", 5, 100, 20, 5)
    enable_stream = st.checkbox("Stream Reasoning (placeholder)", value=True)
    show_plan = st.checkbox("Show Parsed Plan", value=True)
    show_steps = st.checkbox("Show Step Outputs", value=True)
    show_internal_messages = st.checkbox("Show Internal LLM Messages", value=False)
    temperature = st.slider("LLM Temperature", 0.0, 1.2, 0.3, 0.05)
    st.markdown("---")
    st.caption("API key precedence: secrets.toml > environment")

# ------------------------------------------------------------------------------------
# Data Upload / Selection
# ------------------------------------------------------------------------------------
st.subheader("1. Upload / Select Dataset")

uploaded = st.file_uploader("Upload CSV or Parquet file", type=["csv", "parquet"])
sample_choice = st.selectbox(
    "Or load a sample dataset",
    ["None", "iris", "tips", "gapminder (small extract)"]
)

df: Optional[pd.DataFrame] = None
if uploaded:
    try:
        if uploaded.name.lower().endswith(".csv"):
            df = pd.read_csv(uploaded)
        else:
            df = pd.read_parquet(uploaded)
        st.success(f"Loaded file: {uploaded.name} | Rows: {len(df)} | Cols: {len(df.columns)}")
    except Exception as e:
        st.error(f"Failed loading file: {e}")

elif sample_choice != "None":
    if sample_choice == "iris":
        df = px.data.iris()
    elif sample_choice == "tips":
        df = px.data.tips()
    elif sample_choice.startswith("gapminder"):
        d = px.data.gapminder()
        df = d[d["year"] == 2007].head(200)
    st.success(f"Loaded sample: {sample_choice} | Rows: {len(df)} | Cols: {len(df.columns)}")

if df is None:
    st.warning("Upload or select a sample dataset to continue.")
    st.stop()

with st.expander("Data Preview", expanded=True):
    st.dataframe(df.head(max_rows_preview))
    st.caption(f"Total rows: {len(df)} | Columns: {list(df.columns)}")

# ------------------------------------------------------------------------------------
# Profiling (cached)
# ------------------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def cached_profile(frame: pd.DataFrame):
    return build_profile(frame)

profile = cached_profile(df)
with st.expander("Dataset Profile"):
    st.json(profile)

# ------------------------------------------------------------------------------------
# Agent Setup
# ------------------------------------------------------------------------------------
data_context = DataContext(df=df, profile=profile)
agent_cfg = AgentConfig(
    model=model_choice,
    temperature=temperature,
    stream=enable_stream,
    max_context_messages=12
)
agent = DataAnalystAgent(config=agent_cfg)

# ------------------------------------------------------------------------------------
# User Query Input
# ------------------------------------------------------------------------------------
st.subheader("2. Ask a Question")
default_query = "What are the key insights and any anomalies for the numeric columns?"
user_query = st.text_area("Natural Language Question", default_query, height=120)

run_btn = st.button("Run Analysis", type="primary")

# ------------------------------------------------------------------------------------
# Execution
# ------------------------------------------------------------------------------------
if run_btn and user_query.strip():
    try:
        t0 = time.time()
        with st.spinner("Planning..."):
            plan: AnalysisPlan = agent.plan(user_query, data_context)
        if show_plan:
            st.markdown("#### Parsed Plan")
            st.code(plan.model_dump_json(indent=2), language="json")

        tool_results: List[ToolInvocationResult] = []
        if plan.steps:
            st.markdown("#### Executing Steps")
        for i, step in enumerate(plan.steps, start=1):
            step_container = st.container()
            with step_container:
                st.markdown(f"**Step {i}: {step.tool}** – {step.description or ''}")

                if step.tool == "get_schema":
                    res = ToolInvocationResult(
                        tool=step.tool,
                        success=True,
                        output={"schema": profile["schema"]}
                    )
                elif step.tool == "summarize_column":
                    col = step.args.get("column")
                    summary = summarize_column(df, col)
                    res = ToolInvocationResult(
                        tool=step.tool,
                        success=True,
                        output=summary
                    )
                elif step.tool == "run_query":
                    query_text = step.args.get("query")
                    data_out, msg = run_dataframe_query(df, query_text)
                    success = data_out is not None
                    sample_records = (
                        data_out.head(20).to_dict(orient="records") if success else None
                    )
                    res = ToolInvocationResult(
                        tool=step.tool,
                        success=success,
                        output={
                            "rows": sample_records,
                            "info": msg,
                            "row_count": len(data_out) if success else 0
                        },
                        error=None if success else msg
                    )
                elif step.tool == "detect_anomalies":
                    anomalies = detect_anomalies(df, step.args.get("columns"))
                    res = ToolInvocationResult(
                        tool=step.tool,
                        success=True,
                        output={"anomalies": anomalies}
                    )
                elif step.tool == "generate_chart":
                    chart_col = step.args.get("column")
                    chart_type = step.args.get("chart_type", "histogram")
                    cs: ChartSpec = generate_chart_df(df, chart_col, chart_type)
                    res = ToolInvocationResult(
                        tool=step.tool,
                        success=True,
                        output=cs.model_dump()
                    )
                    # Render chart
                    if cs.kind == "histogram":
                        fig = px.histogram(df, x=cs.column, nbins=cs.bins or 30, title=cs.title)
                        st.plotly_chart(fig, use_container_width=True)
                    elif cs.kind == "bar":
                        vc = df[cs.column].value_counts().head(25)
                        fig = px.bar(
                            x=vc.index, y=vc.values,
                            title=cs.title,
                            labels={"x": cs.column, "y": "count"}
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    elif cs.kind == "box":
                        fig = px.box(df, y=cs.column, title=cs.title)
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    res = ToolInvocationResult(
                        tool=step.tool,
                        success=False,
                        error=f"Unknown tool: {step.tool}",
                        output=None
                    )

                tool_results.append(res)
                if show_steps:
                    st.code(res.model_dump_json(indent=2), language="json")

        with st.spinner("Synthesizing final answer..."):
            final_answer: FinalAnswer = agent.finalize_answer(
                user_query,
                plan,
                tool_results,
                data_context
            )

        st.markdown("### ✅ Final Answer")
        st.write(final_answer.answer)

        if final_answer.key_points:
            st.markdown("**Key Points:**")
            for kp in final_answer.key_points:
                st.markdown(f"- {kp}")

        if final_answer.follow_up_questions:
            st.markdown("**Possible Follow-up Questions:**")
            for q in final_answer.follow_up_questions:
                st.markdown(f"- {q}")

        elapsed = time.time() - t0
        st.caption(f"Completed in {elapsed:.2f}s")

        if show_internal_messages:
            st.markdown("### Internal LLM Exchanges")
            for m in agent.history_messages:
                st.write(f"**{m.role.upper()}**")
                st.code(m.content, language="markdown")

    except Exception as e:
        st.error(f"Agent run failed: {e}")
        with st.expander("Traceback"):
            st.code("".join(traceback.format_exc()))
else:
    st.info("Enter a question and click 'Run Analysis'.")

# ------------------------------------------------------------------------------------
# Footer
# ------------------------------------------------------------------------------------
st.markdown("---")
st.caption("Key source: .streamlit/secrets.toml or OPENAI_API_KEY env • Extend tools in agent_tools.py • Logic in agent_runner.py")
ubuntu@ip-172-30-2-118:~/data_analyst_agent$ vi app.py 

                    )

                tool_results.append(res)
                if show_steps:
                    st.code(res.model_dump_json(indent=2), language="json")

        with st.spinner("Synthesizing final answer..."):
            final_answer: FinalAnswer = agent.finalize_answer(
                user_query,
                plan,
                tool_results,
                data_context
            )

        st.markdown("### ✅ Final Answer")
        st.write(final_answer.answer)

        if final_answer.key_points:
            st.markdown("**Key Points:**")
            for kp in final_answer.key_points:
                st.markdown(f"- {kp}")

        if final_answer.follow_up_questions:
            st.markdown("**Possible Follow-up Questions:**")
            for q in final_answer.follow_up_questions:
                st.markdown(f"- {q}")

        elapsed = time.time() - t0
        st.caption(f"Completed in {elapsed:.2f}s")

        if show_internal_messages:
            st.markdown("### Internal LLM Exchanges")
            for m in agent.history_messages:
                st.write(f"**{m.role.upper()}**")
                st.code(m.content, language="markdown")

    except Exception as e:
        st.error(f"Agent run failed: {e}")
        with st.expander("Traceback"):
            st.code("".join(traceback.format_exc()))
else:
    st.info("Enter a question and click 'Run Analysis'.")

                                                                                                                                                                                              301,135-131   Bot
