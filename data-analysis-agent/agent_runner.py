import os
import json
from typing import List, Dict, Any
from dataclasses import dataclass
import httpx

from agent_models import (
    AnalysisPlan,
    PlanStep,
    ToolInvocationResult,
    FinalAnswer,
    LLMMessage
)
from agent_tools import DataContext


@dataclass
class AgentConfig:
    model: str = "gpt-4o-mini"
    temperature: float = 0.3
    stream: bool = False
    max_context_messages: int = 10


class DataAnalystAgent:
    def __init__(self, config: AgentConfig):
        self.cfg = config
        self.history_messages: List[LLMMessage] = []

    def _chat_completion(self, messages: List[Dict[str, str]], response_format: str = "text") -> str:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set.")
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        extra = {}
        if response_format == "json":
            extra["response_format"] = {"type": "json_object"}

        payload = {
            "model": self.cfg.model,
            "temperature": self.cfg.temperature,
            "messages": messages,
            **extra
        }
        with httpx.Client(timeout=90.0) as client:
            r = client.post(url, headers=headers, json=payload)
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"]

    def plan(self, user_query: str, context: DataContext) -> AnalysisPlan:
        schema_overview = [
            {
                "name": c["name"],
                "dtype": c["dtype"],
                "unique": c["unique"],
                "nulls": c["nulls"]
            } for c in context.profile["schema"]
        ]
        sys_prompt = (
            "You are a data analysis planning assistant. "
            "You MUST output a JSON object with keys: intent, rationale, steps. "
            "Each step has: step_id, tool, description, args.\n"
            "Allowed tools:\n"
            "- get_schema: no args\n"
            "- summarize_column: args {column}\n"
            "- run_query: args {query}\n"
            "- detect_anomalies: optional args {columns:[...]}\n"
            "- generate_chart: args {column, chart_type in ['histogram','bar','box']}\n"
            "Keep steps under 6, only what is needed."
        )
        user_prompt = (
            f"User question: {user_query}\n"
            f"Dataset schema summary: {json.dumps(schema_overview)[:4000]}"
        )
        messages = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt}
        ]
        raw = self._chat_completion(messages, response_format="json")
        self.history_messages.append(LLMMessage(role="system", content=sys_prompt))
        self.history_messages.append(LLMMessage(role="user", content=user_prompt))
        self.history_messages.append(LLMMessage(role="assistant", content=raw))

        try:
            plan_json = json.loads(raw)
        except json.JSONDecodeError as e:
            plan_json = {
                "intent": user_query,
                "rationale": f"Failed to parse JSON: {e}",
                "steps": [{"step_id": 1, "tool": "get_schema", "description": "Fallback schema retrieval", "args": {}}]
            }
       steps = []
        for i, s in enumerate(plan_json.get("steps", []), start=1):
            tool = s.get("tool", "get_schema")
            desc = s.get("description") or f"Execute {tool}"
            args = s.get("args", {}) or {}
            steps.append(PlanStep(step_id=i, tool=tool, description=desc, args=args))
        if not steps:
            steps = [PlanStep(step_id=1, tool="get_schema", description="Default schema retrieval", args={})]

        return AnalysisPlan(
            intent=plan_json.get("intent", user_query),
            rationale=plan_json.get("rationale", "No rationale provided."),
            steps=steps
        )

    def finalize_answer(
        self,
        user_query: str,
        plan: AnalysisPlan,
        tool_results: List[ToolInvocationResult],
        context: DataContext
    ) -> FinalAnswer:
        condensed = []
        for tr in tool_results:
            condensed.append({
                "tool": tr.tool,
                "success": tr.success,
                "output": tr.output if tr.success else tr.error
            })

        sys_prompt = (
            "You are a senior data analyst. Produce a JSON object with keys: "
            "answer, key_points (list), follow_up_questions (list). Be concise yet complete."
        )
        user_payload = {
            "question": user_query,
            "plan": plan.model_dump(),
            "results": condensed
        }
        messages = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": json.dumps(user_payload)[:16000]}
        ]
        raw = self._chat_completion(messages, response_format="json")
        self.history_messages.append(LLMMessage(role="assistant", content=raw))
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            data = {
                "answer": raw[:4000],
                "key_points": [],
                "follow_up_questions": []
            }
        return FinalAnswer(
            answer=data.get("answer", raw[:4000]),
            key_points=data.get("key_points", []),
            follow_up_questions=data.get("follow_up_questions", [])
        )
