from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


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


class FinalAnswer(BaseModel):
    answer: str
    key_points: List[str] = Field(default_factory=list)
    follow_up_questions: List[str] = Field(default_factory=list)


class LLMMessage(BaseModel):
    role: str
    content: str
