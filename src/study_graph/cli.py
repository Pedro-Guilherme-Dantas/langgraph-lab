import argparse
import sys
import uuid

from langgraph.types import Command

from study_graph.agents import DemoStudyAgents, LLMStudyAgents
from study_graph.config import load_settings
from study_graph.graph import build_graph


def parse_args() -> argparse.Namespace:
    settings = load_settings()
    parser = argparse.ArgumentParser(description="Cria e revisa uma trilha de estudos.")
    parser.add_argument("--goal", help="Objetivo de aprendizado")
    parser.add_argument("--hours", type=int, default=6, help="Horas disponíveis por semana")
    parser.add_argument(
        "--level",
        choices=("iniciante", "intermediario", "avancado"),
        default="iniciante",
    )
    parser.add_argument("--mode", choices=("demo", "llm"), default=settings.mode)
    parser.add_argument("--model", default=settings.model)
    parser.add_argument("--auto-approve", action="store_true")
    return parser.parse_args()


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    args = parse_args()
    goal = args.goal or input("O que você quer aprender? ").strip()
    if not goal:
        raise SystemExit("Informe um objetivo de estudo.")
    if args.hours < 1:
        raise SystemExit("As horas por semana devem ser maiores que zero.")

    agents = DemoStudyAgents() if args.mode == "demo" else LLMStudyAgents(args.model)
    graph = build_graph(agents)
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    result = graph.invoke(
        {
            "goal": goal,
            "hours_per_week": args.hours,
            "level": args.level,
            "max_revisions": 2,
            "trace": [],
        },
        config,
    )

    while "__interrupt__" in result:
        request = result["__interrupt__"][0].value
        print("\n" + request["plan"])
        review = request["review"]
        print(f"\nRevisor: {review['score']}/10")
        for suggestion in review["suggestions"]:
            print(f"- {suggestion}")

        approved = args.auto_approve or input("\nAprovar plano? [s/N] ").lower() == "s"
        feedback = "" if approved else input("O que deve mudar? ").strip()
        result = graph.invoke(Command(resume={"approved": approved, "feedback": feedback}), config)

    print(f"\nStatus: {result['status']}")
    print("Fluxo: " + " → ".join(result["trace"]))
    if result["status"] == "approved":
        print("\n" + result["final_document"])


if __name__ == "__main__":
    main()
