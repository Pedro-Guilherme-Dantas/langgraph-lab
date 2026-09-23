from langgraph.types import Command

from study_graph.agents import DemoStudyAgents
from study_graph.graph import build_graph


def initial_state() -> dict:
    return {
        "goal": "Aprender LangChain, LangGraph e orquestração de agentes",
        "hours_per_week": 6,
        "level": "iniciante",
        "max_revisions": 2,
        "trace": [],
    }


def test_graph_revises_plan_and_pauses_for_human_review() -> None:
    graph = build_graph(DemoStudyAgents())
    config = {"configurable": {"thread_id": "review-test"}}

    result = graph.invoke(initial_state(), config)

    assert result["revision_count"] == 1
    assert result["review"]["approved"] is True
    assert "__interrupt__" in result
    assert result["trace"] == [
        "resources_discovered",
        "plan_drafted",
        "plan_reviewed",
        "plan_revised",
        "plan_reviewed",
    ]


def test_graph_resumes_after_approval() -> None:
    graph = build_graph(DemoStudyAgents())
    config = {"configurable": {"thread_id": "approval-test"}}
    graph.invoke(initial_state(), config)

    result = graph.invoke(Command(resume={"approved": True}), config)

    assert result["status"] == "approved"
    assert result["final_document"].startswith("# Trilha prática")
    assert result["trace"][-2:] == ["human_approved", "workflow_approved"]


def test_human_can_request_one_more_revision() -> None:
    graph = build_graph(DemoStudyAgents())
    config = {"configurable": {"thread_id": "feedback-test"}}
    graph.invoke(initial_state(), config)

    result = graph.invoke(
        Command(resume={"approved": False, "feedback": "Adicione mais prática."}), config
    )

    assert result["revision_count"] == 2
    assert "__interrupt__" in result
    assert "human_requested_changes" in result["trace"]
