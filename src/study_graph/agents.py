from __future__ import annotations

from typing import Protocol

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage

from study_graph.domain import PlanReview, StudyPlan, StudyWeek


class StudyAgents(Protocol):
    def create_plan(
        self,
        *,
        goal: str,
        hours_per_week: int,
        level: str,
        resources: list[str],
        previous_plan: StudyPlan | None = None,
        feedback: list[str] | None = None,
    ) -> StudyPlan: ...

    def review_plan(self, *, plan: StudyPlan, goal: str, hours_per_week: int) -> PlanReview: ...


class DemoStudyAgents:
    """Implementação determinística para explorar o grafo sem custos de API."""

    def create_plan(
        self,
        *,
        goal: str,
        hours_per_week: int,
        level: str,
        resources: list[str],
        previous_plan: StudyPlan | None = None,
        feedback: list[str] | None = None,
    ) -> StudyPlan:
        is_revision = previous_plan is not None
        practice = (
            "Implemente o incremento, execute os testes e registre as decisões no diário."
            if is_revision
            else "Implemente um pequeno incremento do projeto."
        )
        evidence = (
            "Código executável, testes passando e uma nota curta explicando as escolhas."
            if is_revision
            else "Código executável do incremento da semana."
        )
        focus = [
            ("Fundamentos e estado", ["LangChain", "StateGraph", "estado tipado"]),
            ("Nós e roteamento", ["nodes", "edges", "roteamento condicional"]),
            ("Agentes e ferramentas", ["structured output", "tools", "prompts"]),
            ("Persistência e intervenção", ["checkpoints", "interrupt", "Command"]),
        ]
        weeks = [
            StudyWeek(
                number=index,
                objective=objective,
                topics=topics,
                activities=[
                    f"Estude o material oficial por cerca de {max(1, hours_per_week // 3)}h.",
                    practice,
                    f"Consulte: {resources[(index - 1) % len(resources)]}",
                ],
                evidence=evidence,
            )
            for index, (objective, topics) in enumerate(focus, start=1)
        ]
        return StudyPlan(
            title=f"Trilha prática: {goal}",
            strategy=(
                f"Plano de 4 semanas para nível {level}, com {hours_per_week}h semanais. "
                "Cada semana combina teoria, implementação e uma evidência verificável."
            ),
            weeks=weeks,
        )

    def review_plan(self, *, plan: StudyPlan, goal: str, hours_per_week: int) -> PlanReview:
        has_tests = any("testes" in week.evidence.lower() for week in plan.weeks)
        if not has_tests:
            return PlanReview(
                approved=False,
                score=7,
                issues=["As evidências não incluem uma forma objetiva de verificação."],
                suggestions=["Inclua testes e um registro curto das decisões em cada semana."],
            )
        return PlanReview(
            approved=True,
            score=9,
            suggestions=["Reavalie a carga horária ao final de cada semana."],
        )


class LLMStudyAgents:
    def __init__(self, model_name: str) -> None:
        model = init_chat_model(model_name, temperature=0)
        self._planner = model.with_structured_output(StudyPlan)
        self._reviewer = model.with_structured_output(PlanReview)

    def create_plan(
        self,
        *,
        goal: str,
        hours_per_week: int,
        level: str,
        resources: list[str],
        previous_plan: StudyPlan | None = None,
        feedback: list[str] | None = None,
    ) -> StudyPlan:
        context = ""
        if previous_plan:
            context = (
                f"\nPlano anterior:\n{previous_plan.model_dump_json(indent=2)}"
                f"\nFeedback a resolver:\n{feedback or []}"
            )
        messages = [
            SystemMessage(
                content=(
                    "Você é um planejador de estudos. Crie um plano curto, progressivo, "
                    "prático e compatível com o tempo disponível. Toda semana precisa "
                    "produzir uma evidência observável. Use somente os recursos fornecidos."
                )
            ),
            HumanMessage(
                content=(
                    f"Objetivo: {goal}\nNível: {level}\nHoras por semana: {hours_per_week}"
                    f"\nRecursos: {resources}{context}"
                )
            ),
        ]
        return self._planner.invoke(messages)

    def review_plan(self, *, plan: StudyPlan, goal: str, hours_per_week: int) -> PlanReview:
        return self._reviewer.invoke(
            [
                SystemMessage(
                    content=(
                        "Você é um revisor exigente. Aprove apenas se o plano for progressivo, "
                        "couber no tempo, tiver prática e evidências verificáveis. Liste problemas "
                        "e sugestões específicas; não reescreva o plano."
                    )
                ),
                HumanMessage(
                    content=(
                        f"Objetivo: {goal}\nHoras semanais: {hours_per_week}"
                        f"\nPlano:\n{plan.model_dump_json(indent=2)}"
                    )
                ),
            ]
        )
