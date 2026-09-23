# Guia para agentes de código

Este repositório é um laboratório didático. Prefira clareza e conceitos explícitos
a abstrações genéricas ou infraestrutura de produção.

## Objetivo do projeto

Demonstrar um workflow LangGraph que realmente exige grafo: estado compartilhado,
roteamento condicional, ciclo de revisão limitado, checkpoint e human-in-the-loop.
O modo `demo` deve continuar funcional sem rede e sem credenciais.

## Invariantes

- O domínio não importa LangGraph; schemas e renderização ficam em `domain.py`.
- Agentes dependem de modelos do domínio, não do estado completo do grafo.
- Nós retornam apenas atualizações de estado. Não mutam o objeto recebido.
- Estado guarda dados, nunca prompts prontos.
- Todo ciclo deve ter um limite explícito.
- Efeitos externos devem ficar isolados em tools ou adapters substituíveis.
- Testes não podem fazer chamadas de rede nem depender de chaves de API.
- Não adicione API web, banco, Docker ou observabilidade sem um caso de estudo claro.

## Ao alterar o fluxo

1. Atualize o diagrama e a tabela em `docs/architecture.md`.
2. Cubra novas rotas com agentes determinísticos.
3. Execute `uv run pytest`, `uv run ruff check .` e
   `uv run ruff format --check .`.
4. Confirme que o comando documentado no README continua funcionando.

