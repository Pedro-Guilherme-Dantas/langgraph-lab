from langchain.tools import tool

RESOURCE_CATALOG = {
    "langchain": [
        "LangChain Overview — https://docs.langchain.com/oss/python/langchain/overview",
        "Models — https://docs.langchain.com/oss/python/langchain/models",
        "Tools — https://docs.langchain.com/oss/python/langchain/tools",
    ],
    "langgraph": [
        "LangGraph Overview — https://docs.langchain.com/oss/python/langgraph/overview",
        "Thinking in LangGraph — https://docs.langchain.com/oss/python/langgraph/thinking-in-langgraph",
        "Persistence — https://docs.langchain.com/oss/python/langgraph/persistence",
    ],
    "agentes": [
        "Agents — https://docs.langchain.com/oss/python/langchain/agents",
        "Human-in-the-loop — https://docs.langchain.com/oss/python/langchain/human-in-the-loop",
    ],
}


@tool
def find_learning_resources(topics: list[str]) -> list[str]:
    """Busca recursos oficiais no catálogo local para os tópicos informados.

    Use esta ferramenta antes de criar um plano para que as atividades apontem
    para material confiável. Retorna uma lista sem duplicatas.
    """
    normalized = " ".join(topics).lower()
    matches = [
        resource
        for topic, resources in RESOURCE_CATALOG.items()
        if topic in normalized
        for resource in resources
    ]
    if not matches:
        matches = RESOURCE_CATALOG["langgraph"]
    return list(dict.fromkeys(matches))
