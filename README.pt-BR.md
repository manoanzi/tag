# TAG — The Architecture of Gateways

**Um padrão de arquitetura pragmático, funcional e centrado em domínio para microsserviços em Python, incluindo serviços agênticos (LLM).**

[![CI](https://github.com/manoanzi/tag/actions/workflows/ci.yml/badge.svg)](https://github.com/manoanzi/tag/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

🇺🇸 [Read in English](README.md)

> Inspirado em Arquitetura Hexagonal, na arquitetura Diplomata do Nubank e no DOMA da Uber.

---

## Por que TAG

Quando cada time estrutura serviços de um jeito, trocar de contexto custa caro: o onboarding demora, o code review vira debate sobre onde o código deve ficar e o custo de manutenção cresce a cada novo serviço.

O TAG dá a todo serviço o mesmo formato. Quem conhece um serviço TAG se localiza em qualquer outro. Isso importa principalmente para pessoas menos seniores e para áreas que mudam rápido, como GenAI, onde agentes, ferramentas e integrações mudam toda semana.

Ele nasce de experiências em ambientes bem diferentes: construir uma startup de pagamentos do zero, trabalhar nos serviços padronizados em Clojure do Nubank e construir plataformas agênticas como Staff Engineer em GenAI.

## O que é TAG

- **Visão estratégica** (do DOMA): serviços agrupados por domínio de negócio, com gateways como pontos de entrada que escondem os detalhes internos de cada domínio.
- **Visão tática** (do Diplomata e da Hexagonal): todo serviço tem as mesmas camadas, então o código é previsível entre times.

Pilares:

- **Programação funcional:** imutabilidade, funções puras e composição via pipelines
- **Domínio primeiro:** regras de negócio isoladas no centro
- **Tratamento de erros orientado a trilhos:** tipos `Result` no lugar de exceções
- **Injeção de dependência via Protocol:** testável sem infraestrutura
- **Agnóstico de transporte:** HTTP, gRPC, mensageria, streaming ou tool call de um LLM

## Exemplo executável

[`examples/user-service`](examples/user-service) é um serviço completo com todas as camadas do TAG (FastAPI + SQLite, sem infraestrutura externa), com testes unitários, de integração e HTTP:

```bash
cd examples/user-service && pip install -e ".[dev]" && pytest && python -m src.main
```

## Princípios

| # | Princípio | Em resumo |
|---|---|---|
| 1 | Protocols definem contratos | Toda dependência de infraestrutura fica atrás de um `typing.Protocol` |
| 2 | Domains são schemas, nunca funções | Definições de dados imutáveis (Pydantic, `frozen=True`) |
| 3 | Logics são puras e concentram as decisões | Sem IO, sem aleatoriedade, sem relógio. Toda regra e ramificação (validação, mapeamento de status) fica aqui |
| 4 | Adapters transformam estruturas | Conversões puras entre camadas, inclusive `model_dump`, linhas do banco e erros. Nada de `uuid4()` ou `now()` |
| 5 | Gateways fazem IO | Toda comunicação externa, via Protocols recebidos como parâmetro |
| 6 | Flows são pipelines de orquestração | Um Flow por caso de uso, compondo Gateways, Logics e Adapters |
| 7 | Handlers conectam transporte a Flows | Encadeiam Adapter → Flow → Logic, sem `if` nem `match` |
| 8 | Drivers implementam Protocols | Bibliotecas externas ficam fora do código de domínio |
| 9 | Efeitos colaterais nas bordas | IO, aleatoriedade e tempo vêm de Protocols (ex.: `IdGeneratorProtocol`), acessados por Gateways |

Nomes: contratos são `<Capacidade>Protocol` (`DatabaseProtocol`, `LoggerProtocol`) e suas implementações são `<Tecnologia>Driver` (`SQLiteDriver`, `UUID4Driver`).

## Estrutura de diretórios

```
project-root/
├── src/
│   ├── protocols/   # contratos de infraestrutura (typing.Protocol)
│   ├── domains/     # entidades e objetos de valor (Pydantic)
│   ├── resources/   # configs, queries, schemas estáticos
│   ├── logics/      # funções puras de domínio
│   ├── adapters/    # transformações de dados entre camadas
│   ├── gateways/    # IO via Protocols
│   ├── flows/       # pipelines de casos de uso, por domínio
│   ├── handlers/    # pontos de entrada (HTTP, Kafka, cron, tools de agente)
│   └── main.py      # composição
├── drivers/         # implementações de bibliotecas, fora do src/
└── tests/
    ├── unit/        # Adapters e Logics
    └── integration/ # Flows com Protocols em memória
```

## Regras de dependência

| Camada | Pode chamar |
|---|---|
| Protocols, Domains, Resources | nenhuma |
| Logics, Adapters | Domains |
| Gateways | Protocols, Domains, Adapters, Resources |
| Flows | Gateways, Logics, Adapters, Protocols, Resources |
| Handlers | Adapters, Flows, Logics, Protocols, Resources |
| Drivers | Protocols, Resources |
| `main.py` | Drivers, Handlers, Resources |

```
Request → Driver → Handler → Adapter → Flow → Gateway → Protocol (IO)
                                          ↘ Logic (puro)
Response ← Driver ← Handler ← Result ←────┘
```

## Exemplo: um caso de uso como Flow

```python
# src/flows/user/create_user_flow.py
def create_user_flow(
    db: DatabaseProtocol, ids: IdGeneratorProtocol, data: CreateUserInput
) -> Result[CreateUserOutput, UserError]:
    return flow(
        validate_email_domain(data.email),                       # Logic (pure)
        bind(lambda email: find_users_by_email(db, email)),      # Gateway (IO)
        bind(ensure_user_not_exists),                            # Logic (pure)
        bind(lambda _: generate_user_id(ids)),                   # Gateway (randomness)
        map_(lambda user_id: to_user_domain(data, user_id)),     # Adapter
        map_(to_user_record),                                    # Adapter
        bind(lambda record: persist_user(db, record)),           # Gateway (IO)
        map_(to_create_user_output),                             # Adapter
    )
```

O Flow depende só de Protocols. Até o id do usuário vem do `IdGeneratorProtocol`, então todo Adapter e toda Logic continuam puros e os testes são determinísticos. O [exemplo executável](examples/user-service) injeta Drivers de SQLite e UUIDv4; os testes injetam um banco em memória e um id fixo.

O Handler não tem ramificação: a decisão sobre a resposta é de uma Logic, e o corpo da resposta é montado por um Adapter.

```python
# src/handlers/user_handlers.py: no if, no match
def handle_create_user(db, ids, logger, raw_body) -> tuple[int, dict]:
    result = to_create_user_input(raw_body).bind(lambda data: create_user_flow(db, ids, data))
    result.alt(tap(lambda error: logger.error("could not create user", error=error.name)))
    return resolve_create_user_status(result), to_create_user_response_body(result)  # Logic, Adapter
```

```python
# src/main.py
def create_app() -> FastAPIDriver:
    settings = load_settings()
    db, ids, logger, http = SQLiteDriver(settings), UUID4Driver(), StdoutLoggerDriver(), FastAPIDriver()
    register_user_handlers(http, db, ids, logger)
    return http
```

Trocar a infraestrutura é mudar uma linha no `main.py`. Uma tool de agente LLM é só mais um Handler chamando o mesmo Flow.

## Estratégia de testes

| Tipo | Cobre | Infraestrutura |
|---|---|---|
| Unitário | Adapters e Logics (funções puras) | Nenhuma |
| Integração | Flows completos | Protocols falsos, em memória |

Você testa fluxo e regra de negócio, não bibliotecas. A suíte roda sem containers.

## Tratamento de erros

Toda operação que pode falhar retorna `Result[Sucesso, Falha]` ([dry-python/returns](https://github.com/dry-python/returns)). Num pipeline, a primeira falha propaga até o final, sem try/except em cada etapa. O `@safe` encapsula código que lança exceções, como a validação do Pydantic nos Adapters de entrada.

## Evolução de contratos

Adapters de entrada seguem o padrão **Tolerant Reader**: leem só os campos de que precisam, então serviços upstream podem adicionar campos sem quebrar consumidores. Contratos externos podem ser declarados em `resources/` e validados no CI.

## Comparação

| | TAG | Hexagonal | Arquitetura Limpa | DOMA | Diplomata |
|---|---|---|---|---|---|
| Paradigma | Funcional | Agnóstico | OOP | Agnóstico | Funcional (Clojure) |
| Escopo | Serviço + organização | Serviço | Serviço | Organização | Serviço |
| Tratamento de erros | Result | — | — | — | — |
| Injeção de dependência | Protocols | Portas | Interfaces | — | Componentes |

## FAQ

<details><summary><strong>Funciona com qualquer framework HTTP?</strong></summary>

Sim. O framework é um Driver atrás do `HttpServerProtocol`. FastAPI, Flask ou Starlette são trocados no `main.py`.
</details>

<details><summary><strong>Serve para monólitos?</strong></summary>

Sim. Cada domínio ganha sua pasta em `flows/`, e os Protocols mantêm os domínios desacoplados da infraestrutura.
</details>

<details><summary><strong>E async?</strong></summary>

Protocols podem declarar métodos assíncronos, e a `returns` oferece `FutureResult` para operações async que podem falhar.
</details>

## Contribuindo

Contribuições são bem-vindas. Veja o [CONTRIBUTING.md](CONTRIBUTING.md).

## Licença

MIT. Veja [LICENSE](LICENSE).
