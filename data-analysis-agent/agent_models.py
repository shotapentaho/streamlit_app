# v13 — FinalAnswer validation fix for Pydantic v2.9
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


class PlanStep(BaseModel):
    step_id: int
    tool: str = Field(..., description="Name of the tool function to run")
    description: Optional[str] = Field(None, description="Human readable step description")
    args: Dict[str, Any] = Field(default_factory=dict)


class AnalysisPlan(BaseModel):
    intent: str
    rationale: str
    steps: List[PlanStep]


class ToolInvocationResult(BaseModel):
    tool: str
    success: bool
    output: Optional[Any] = None
    error: Optional[str] = None


class ChartSpec(BaseModel):
    kind: str
    column: str
    title: str
    bins: Optional[int] = None
    chart_type: Optional[str] = None  # for compatibility


def _stringify(value: Any) -> str:
    """
    Convert dicts/lists (often returned by LLMs) into readable text.
    Special-cases keys like 'insights' and 'anomalies' for nicer formatting.
    """
    try:
        if isinstance(value, dict):
            parts: List[str] = []

            if "insights" in value:
                parts.append("Insights:")
                ins = value.get("insights")
                if isinstance(ins, dict):
                    for k, v in ins.items():
                        parts.append(f"- {k}: {v}")
                else:
                    parts.append(f"- {ins}")

            if "anomalies" in value:
                if parts:
                    parts.append("")  # blank line
                parts.append("Anomalies:")
                an = value.get("anomalies")
                if isinstance(an, dict):
                    for k, v in an.items():
                        parts.append(f"- {k}: {v}")
                elif isinstance(an, list):
                    preview = ", ".join(map(str, an[:20]))
                    more = f" (+{len(an)-20} more)" if len(an) > 20 else ""
                    parts.append(f"- indices: {preview}{more}")
                else:
                    parts.append(f"- {an}")

            if parts:
                return "\n".join(parts)

            # Generic dict pretty-print
            return "\n".join(f"- {k}: {v}" for k, v in value.items())

        if isinstance(value, list):
            # Inline for simple scalars; bullets for complex objects
            if all(isinstance(x, (int, float, str)) for x in value):
                return ", ".join(map(str, value))
            return "\n".join(f"- {x}" for x in value)

        return str(value)
    except Exception:
        return str(value)


class FinalAnswer(BaseModel):
    answer: str
    key_points: List[str] = Field(default_factory=list)
    follow_up_questions: List[str] = Field(default_factory=list)

    @field_validator("answer", mode="before")
    @classmethod
    def _coerce_answer_to_str(cls, v: Any) -> str:
        # Accept dict/list/etc. and render to human-readable text to avoid validation errors.
        if isinstance(v, str):
            return v
        return _stringify(v)

    @field_validator("key_points", "follow_up_questions", mode="before")
    @classmethod
    def _normalize_list_of_str(cls, v: Any) -> List[str]:
        # Ensure these fields are always lists of strings.
        if v is None:
            return []
        if isinstance(v, list):
            return [str(x) for x in v]
        if isinstance(v, str):
            return [v]
        if isinstance(v, dict):
            return [f"{k}: {val}" for k, val in v.items()]
        return [str(v)]


class LLMMessage(BaseModel):
    role: str
    content: str