# TAG — The Architecture of Gateways

**A pragmatic, functional and domain-centric architecture pattern for Python microservices, including agentic (LLM) services.**

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

🇧🇷 [Leia em português](README.pt-BR.md)

> Inspired by Hexagonal Architecture, Nubank's Diplomat architecture and Uber's DOMA.

---

## Why TAG

When every team structures services differently, switching context is expensive: onboarding is slow, reviews turn into debates about where code goes, and maintenance cost grows with every new service.

TAG gives every service the same shape. Anyone who knows one TAG service can find their way around any other, which matters most for less-senior engineers and for fast-moving areas like GenAI, where agents, tools and integrations change every week.

It comes from experience across very different environments: building a payments startup from scratch, working inside Nubank's standardized Clojure services, and building agentic platforms as a Staff Engineer in GenAI.

## What TAG is

- **Strategic view** (from DOMA): services are grouped by business domain, with gateways as the entry points that hide each domain's internals.
- **Tactical view** (from Diplomat and Hexagonal): every service has the same layers, so code is predictable across teams.

Core pillars:

- **Functional programming:** immutability, pure functions and composition through pipelines
- **Domain first:** business rules isolated at the center
- **Railway-oriented error handling:** `Result` types instead of exceptions
- **Protocol-based dependency injection:** testable without infrastructure
- **Transport-agnostic:** HTTP, gRPC, messaging, streaming or an LLM tool call

## Runnable example

[`examples/user-service`](examples/user-service) is a complete service built with every TAG layer (FastAPI + SQLite, no external infrastructure), with unit, integration and HTTP tests:

```bash
cd examples/user-service && pip install -e ".[dev]" && pytest && python -m src.main
```

## Principles

| # | Principle | In short |
|---|---|---|
| 1 | Protocols define contracts | Every infrastructure dependency sits behind a `typing.Protocol` |
| 2 | Domains are schemas, never functions | Immutable data definitions (Pydantic, `frozen=True`) |
| 3 | Logics are pure | No IO: data in, data out |
| 4 | Adapters transform structures | Pure conversions between layers |
| 5 | Gateways do IO | All external communication, through Protocols received as parameters |
| 6 | Flows are orchestration pipelines | One Flow per use case, composing Gateways, Logics and Adapters |
| 7 | Handlers connect transport to Flows | They own a request's lifecycle, from input to output |
| 8 | Drivers implement Protocols | External libraries live outside the domain code |
| 9 | IO at the edges | The core of the application stays pure |

## Directory structure

```
project-root/
├── src/
│   ├── protocols/   # infrastructure contracts (typing.Protocol)
│   ├── domains/     # entities and value objects (Pydantic)
│   ├── resources/   # settings, queries, static schemas
│   ├── logics/      # pure domain functions
│   ├── adapters/    # data transformations between layers
│   ├── gateways/    # IO through Protocols
│   ├── flows/       # use-case pipelines, organized by domain
│   ├── handlers/    # entry points (HTTP, Kafka, cron, agent tools)
│   └── main.py      # composition root
├── drivers/         # library implementations, outside src/
└── tests/
    ├── unit/        # Adapters and Logics
    └── integration/ # Flows with in-memory Protocols
```

## Dependency rules

| Layer | May call |
|---|---|
| Protocols, Domains, Resources | nothing |
| Logics, Adapters | Domains |
| Gateways | Protocols, Domains, Adapters, Resources |
| Flows | Gateways, Logics, Adapters, Protocols, Resources |
| Handlers | Adapters, Flows, Protocols, Resources |
| Drivers | Protocols, Resources |
| `main.py` | Drivers, Handlers, Resources |

```
Request → Driver → Handler → Adapter → Flow → Gateway → Protocol (IO)
                                          ↘ Logic (pure)
Response ← Driver ← Handler ← Result ←────┘
```

## Example: a use case as a Flow

```python
# src/flows/user/create_user_flow.py
from returns.pipeline import flow
from returns.pointfree import bind, map_
from returns.result import Result, Success

def create_user_flow(db: DatabaseClient, data: CreateUserInput) -> Result[CreateUserOutput, str]:
    return flow(
        validate_email_domain(data.email),                         # Logic (pure)
        bind(lambda email: find_user_by_email(db, email)),         # Gateway (IO)
        bind(ensure_user_not_exists),                              # Logic (pure)
        bind(lambda _: Success(to_user_domain(data))),             # Adapter
        bind(lambda user: persist_user(db, user)),                 # Gateway (IO)
        map_(to_create_user_output),                               # Adapter
    )
```

The Flow depends only on the `DatabaseClient` Protocol. The [runnable example](examples/user-service) injects a SQLite Driver, production could inject a Postgres one, and tests use an in-memory fake.

```python
# src/main.py
def create_app() -> FastAPIDriver:
    settings = load_settings()
    db, logger, http = SQLiteDriver(settings), StdoutLoggerDriver(), FastAPIDriver()
    register_user_handlers(http, db, logger)
    return http
```

Swapping infrastructure means changing one line in `main.py`. An LLM agent tool is just another Handler calling the same Flow.

## Testing strategy

| Type | Covers | Infrastructure |
|---|---|---|
| Unit | Adapters and Logics (pure functions) | None |
| Integration | Full Flows | Fake Protocols, in memory |

You test business flows and rules, not libraries. No containers are needed to run the suite.

## Error handling

Every operation that can fail returns `Result[Success, Failure]` ([dry-python/returns](https://github.com/dry-python/returns)). In a pipeline, the first failure propagates to the end with no try/except at each step. `@safe` wraps code that raises exceptions, such as Pydantic validation in input Adapters.

## Contract evolution

Input Adapters follow the **Tolerant Reader** pattern: they read only the fields they need, so upstream services can add fields without breaking consumers. External contracts can be declared in `resources/` and checked in CI.

## How TAG compares

| | TAG | Hexagonal | Clean Architecture | DOMA | Diplomat |
|---|---|---|---|---|---|
| Paradigm | Functional | Agnostic | OOP | Agnostic | Functional (Clojure) |
| Scope | Service + organization | Service | Service | Organization | Service |
| Error handling | Result | — | — | — | — |
| Dependency injection | Protocols | Ports | Interfaces | — | Components |

## FAQ

<details><summary><strong>Does it work with any HTTP framework?</strong></summary>

Yes. The framework is a Driver behind the `HttpServer` Protocol. FastAPI, Flask or Starlette can be swapped in `main.py`.
</details>

<details><summary><strong>Does it work for monoliths?</strong></summary>

Yes. Each domain gets its own folder under `flows/`, and Protocols keep domains decoupled from infrastructure.
</details>

<details><summary><strong>What about async?</strong></summary>

Protocols can declare async methods, and `returns` provides `FutureResult` for async operations that can fail.
</details>

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT. See [LICENSE](LICENSE).
