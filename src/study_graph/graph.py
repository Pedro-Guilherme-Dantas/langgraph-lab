from __future__ import annotations

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from study_graph.agents import StudyAgents
from study_graph.domain import PlanReview, StudyPlan, StudyState, render_plan
from study_graph.tools import find_learning_resources


def build_graph(agents: StudyAgents, *, checkpointer=None):
    def discover_resources(state: StudyState) -> dict:
        resources = find_learning_resources.invoke(
            {"topics": [state["goal"], "langchain", "langgraph", "agentes"]}
        )
        return {"resources": resources, "trace": ["resources_discovered"]}

    def draft_plan(state: StudyState) -> dict:
        plan = agents.create_plan(
            goal=state["goal"],
            hours_per_week=state["hours_per_week"],
            level=state["level"],
            resources=state["resources"],
        )
        return {
            "plan": plan.model_dump(),
            "revision_count": 0,
            "trace": ["plan_drafted"],
        }

    def review_plan(state: StudyState) -> dict:
        review = agents.review_plan(
            plan=StudyPlan.model_validate(state["plan"]),
            goal=state["goal"],
            hours_per_week=state["hours_per_week"],
        )
        return {"review": review.model_dump(), "trace": ["plan_reviewed"]}

    def revise_plan(state: StudyState) -> dict:
        review = PlanReview.model_validate(state["review"])
        human_feedback = state.get("human_feedback")
        feedback = [*review.issues, *review.suggestions]
        if human_feedback:
            feedback.append(human_feedback)
        plan = agents.create_plan(
            goal=state["goal"],
            hours_per_week=state["hours_per_week"],
            level=state["level"],
            resources=state["resources"],
            previous_plan=StudyPlan.model_validate(state["plan"]),
            feedback=feedback,
        )
        return {
            "plan": plan.model_dump(),
            "revision_count": state.get("revision_count", 0) + 1,
            "human_feedback": "",
            "trace": ["plan_revised"],
        }

    def human_review(state: StudyState) -> Command:
        review = PlanReview.model_validate(state["review"])
        decision = interrupt(
            {
                "question": "Você aprova este plano?",
                "plan": render_plan(StudyPlan.model_validate(state["plan"])),
                "review": review.model_dump(),
            }
        )
        if decision.get("approved"):
            return Command(
                update={"human_approved": True, "trace": ["human_approved"]},
                goto="finalize",
            )
        if state.get("revision_count", 0) < state["max_revisions"]:
            return Command(
                update={
                    "human_approved": False,
                    "human_feedback": decision.get("feedback", "Revise o plano."),
                    "trace": ["human_requested_changes"],
                },
                goto="revise_plan",
            )
        return Command(
            update={"human_approved": False, "trace": ["revision_limit_reached"]},
            goto="finalize",
        )

    def finalize(state: StudyState) -> dict:
        approved = state.get("human_approved", False)
        status = "approved" if approved else "rejected"
        document = render_plan(StudyPlan.model_validate(state["plan"]))
        return {
            "status": status,
            "final_document": document,
            "trace": [f"workflow_{status}"],
        }

    def after_review(state: StudyState) -> str:
        review = PlanReview.model_validate(state["review"])
        if review.approved or state.get("revision_count", 0) >= state["max_revisions"]:
            return "human_review"
        return "revise_plan"

    workflow = StateGraph(StudyState)
    workflow.add_node("discover_resources", discover_resources)
    workflow.add_node("draft_plan", draft_plan)
    workflow.add_node("review_plan", review_plan)
    workflow.add_node("revise_plan", revise_plan)
    workflow.add_node("human_review", human_review)
    workflow.add_node("finalize", finalize)
    workflow.add_edge(START, "discover_resources")
    workflow.add_edge("discover_resources", "draft_plan")
    workflow.add_edge("draft_plan", "review_plan")
    workflow.add_conditional_edges(
        "review_plan",
        after_review,
        {"revise_plan": "revise_plan", "human_review": "human_review"},
    )
    workflow.add_edge("revise_plan", "review_plan")
    workflow.add_edge("finalize", END)
    return workflow.compile(checkpointer=checkpointer or InMemorySaver())
