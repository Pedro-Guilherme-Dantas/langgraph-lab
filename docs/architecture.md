# Arquitetura

## Por que LangGraph

Este workflow não é uma chain linear. O revisor pode devolver o plano ao
planejador, a pessoa pode interromper a execução por tempo indeterminado e a
retomada precisa continuar com o mesmo estado. O grafo torna essas transições
explícitas e inspecionáveis.

## Responsabilidades

| Componente | Responsabilidade | Não deve fazer |
| --- | --- | --- |
| `domain.py` | Schemas, estado e apresentação do plano | Chamar LLM ou LangGraph |
| `agents.py` | Planejar e revisar por interfaces tipadas | Decidir transições do grafo |
| `tools.py` | Isolar acesso a fontes de dados | Guardar estado do workflow |
| `graph.py` | Nós, rotas, ciclos e interrupção | Conhecer CLI ou variáveis de ambiente |
| `cli.py` | Entrada, aprovação e retomada | Implementar regra de negócio |

## Estado por etapa

| Nó | Lê | Escreve | Próximo passo |
| --- | --- | --- | --- |
| `discover_resources` | objetivo | recursos | `draft_plan` |
| `draft_plan` | perfil e recursos | plano, contador | `review_plan` |
| `review_plan` | plano e restrições | parecer | rota condicional |
| `revise_plan` | plano e feedback | novo plano, contador | `review_plan` |
| `human_review` | plano e parecer | decisão/feedback | `finalize` ou `revise_plan` |
| `finalize` | plano e decisão | documento e status | `END` |

O reducer de `trace` é a única operação de combinação customizada. Os demais
campos seguem a regra padrão de sobrescrita do LangGraph.

## Duas implementações de agentes

`DemoStudyAgents` é um fake de domínio, não um mock de teste. Ele permite estudar
o workflow inteiro e reproduzir sempre a mesma rota. Na primeira avaliação ele
reprova o plano; após a correção, aprova.

`LLMStudyAgents` usa o mesmo contrato, `init_chat_model` e saída estruturada com
Pydantic. Como o grafo depende do protocolo `StudyAgents`, trocar modelo ou criar
outro provedor não altera a orquestração.

## Checkpoint e retomada

`InMemorySaver` exige um `thread_id`. Quando `interrupt()` é alcançado, o estado
é salvo e a chamada retorna ao cliente. A CLI coleta a decisão e envia
`Command(resume=...)` usando o mesmo identificador. Em uma aplicação real, apenas
o checkpointer e a camada de entrada precisariam mudar para permitir retomada
entre processos.

