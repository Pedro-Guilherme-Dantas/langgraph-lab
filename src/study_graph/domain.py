from typing import Annotated, Literal, NotRequired, TypedDict

from pydantic import BaseModel, Field


class StudyWeek(BaseModel):
    number: int = Field(ge=1)
    objective: str
    topics: list[str] = Field(min_length=1)
    activities: list[str] = Field(min_length=1)
    evidence: str = Field(description="Resultado observável que comprova o aprendizado")


class StudyPlan(BaseModel):
    title: str
    strategy: str
    weeks: list[StudyWeek] = Field(min_length=1)


class PlanReview(BaseModel):
    approved: bool
    score: int = Field(ge=0, le=10)
    issues: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)


def append_trace(current: list[str], new: list[str]) -> list[str]:
    return [*current, *new]


class StudyState(TypedDict):
    goal: str
    hours_per_week: int
    level: Literal["iniciante", "intermediario", "avancado"]
    max_revisions: int
    resources: NotRequired[list[str]]
    plan: NotRequired[dict]
    review: NotRequired[dict]
    revision_count: NotRequired[int]
    human_feedback: NotRequired[str]
    human_approved: NotRequired[bool]
    status: NotRequired[str]
    final_document: NotRequired[str]
    trace: Annotated[list[str], append_trace]


def render_plan(plan: StudyPlan) -> str:
    lines = [f"# {plan.title}", "", plan.strategy]
    for week in plan.weeks:
        lines.extend(
            [
                "",
                f"## Semana {week.number}: {week.objective}",
                "",
                f"**Tópicos:** {', '.join(week.topics)}",
                "",
                "**Atividades:**",
                *[f"- {activity}" for activity in week.activities],
                "",
                f"**Evidência:** {week.evidence}",
            ]
        )
    return "\n".join(lines)
