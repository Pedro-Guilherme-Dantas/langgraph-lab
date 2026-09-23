# Study Graph

Um projeto pequeno e funcional para estudar **LangChain**, **LangGraph** e
orquestração de agentes. Ele cria uma trilha de estudos, submete o plano a um
agente revisor, aplica correções em um ciclo limitado e pausa para aprovação
humana antes de finalizar.

O caso de uso é propositalmente simples. O LangGraph entra porque existe um
workflow real, com estado, decisões, repetição e pausa/retomada — não apenas uma
sequência linear de chamadas a um modelo.

## Fluxo

```text
START
  │
  ▼
buscar recursos ──► planejar ──► revisar
                                  │
                    reprovado     │ aprovado/limite
                       ┌───────────┴──────────┐
                       ▼                      ▼
                    corrigir           aprovação humana
                       │                │             │
                       └──► revisar ◄───┘ rejeita     │ aprova
                                            │         │
                                            ▼         ▼
                                          corrigir  finalizar ──► END
```

### O que observar no código

- `StudyState` guarda dados brutos compartilhados; prompts são montados nos agentes.
- `trace` usa um reducer para acumular eventos em vez de sobrescrevê-los.
- O revisor decide, por uma aresta condicional, entre corrigir ou pedir aprovação.
- `interrupt()` pausa o grafo; `Command(resume=...)` o retoma no mesmo `thread_id`.
- `Command(goto=...)` expressa a decisão humana junto da atualização do estado.
- O ciclo tem limite (`max_revisions`) para evitar repetição infinita.
- Os agentes usam schemas Pydantic e, no modo LLM, saída estruturada.
- A busca de material é uma tool LangChain local, previsível e fácil de substituir.

## Executar

Pré-requisitos: Python 3.11+ e [uv](https://docs.astral.sh/uv/).

```bash
uv sync --extra dev
uv run study-graph \
  --goal "Aprender LangGraph construindo agentes" \
  --hours 6 \
  --level iniciante
```

O modo padrão é `demo`: não faz chamadas externas, mas percorre todo o grafo,
incluindo uma reprovação automática, correção e aprovação humana. Para uma
execução não interativa:

```bash
uv run study-graph --goal "Aprender LangGraph" --auto-approve
```

### Usar um LLM real

Copie `.env.example` para `.env`, configure sua chave e altere o modo:

```dotenv
STUDY_GRAPH_MODE=llm
STUDY_GRAPH_MODEL=openai:gpt-4.1-mini
OPENAI_API_KEY=sua-chave
```

Também é possível sobrescrever pela CLI:

```bash
uv run study-graph --mode llm --model openai:gpt-4.1-mini \
  --goal "Dominar fluxos com LangGraph"
```

O prefixo `openai:` é interpretado pelo `init_chat_model`. Para outro provedor,
instale a integração correspondente e informe `provedor:modelo`.

## Testes e qualidade

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

Os testes usam os agentes determinísticos e verificam o ciclo de revisão, a
interrupção e a retomada. Assim, eles são rápidos e não dependem de rede ou chave.

## Estrutura

```text
src/study_graph/
├── agents.py   # contrato e implementações dos agentes
├── cli.py      # interface de terminal e retomada
├── config.py   # configuração por ambiente
├── domain.py   # schemas e estado compartilhado
├── graph.py    # nós, arestas e compilação do LangGraph
└── tools.py    # catálogo local exposto como tool
tests/
└── test_graph.py
```

Detalhes sobre limites entre módulos, leitura/escrita do estado e retomada estão
em [docs/architecture.md](docs/architecture.md). Regras para agentes que forem
evoluir este laboratório ficam em [AGENTS.md](AGENTS.md).

Para acompanhar uma execução completa, da entrada na CLI até o `END`, consulte
[docs/complete-flow.md](docs/complete-flow.md). O guia mostra a evolução do
estado, os ciclos, o checkpoint e a retomada com diagramas.

## Caminho de estudo sugerido

1. Execute o modo demo e acompanhe o `trace`.
2. Leia `domain.py` e depois `graph.py`; desenhe as transições à mão.
3. Mude o critério do `DemoStudyAgents.review_plan` e observe a rota.
4. Adicione um campo ao estado e faça dois nós consumi-lo.
5. Troque `InMemorySaver` por um checkpointer persistente.
6. Implemente outro provedor em `LLMStudyAgents` via configuração.

## Decisões e limites

- Não há API web, banco vetorial, Docker ou fila: seriam distrações nesta fase.
- O catálogo local representa uma integração externa sem tornar o exemplo frágil.
- `InMemorySaver` mantém checkpoints apenas durante o processo. Persistência em
  disco é uma evolução natural quando esse conceito já estiver claro.
- Evals, observabilidade e deploy ficam fora do escopo inicial, conforme o foco
  didático do projeto.

## Referências

- [Thinking in LangGraph](https://docs.langchain.com/oss/python/langgraph/thinking-in-langgraph)
- [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview)
- [LangChain models](https://docs.langchain.com/oss/python/langchain/models)
