# TAG — The Architecture of Gateways

**A pragmatic, functional and domain-centric architecture pattern for Python microservices, including agentic (LLM) services.**

[![CI](https://github.com/manoanzi/tag/actions/workflows/ci.yml/badge.svg)](https://github.com/manoanzi/tag/actions/workflows/ci.yml)
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
| 3 | Logics are pure and hold the decisions | No IO, randomness, clock or `Result`. Every rule and branch lives here, and the decision comes back as a domain schema (e.g. `UserRuleCheck`) |
| 4 | Adapters transform structures | Pure conversions between layers: `model_dump`, rows, errors, responses, and schemas to `Result` (`Success`/`Failure`). No `uuid4()` or `now()` |
| 5 | Gateways do IO | All external communication, through Protocols received as parameters |
| 6 | Flows are orchestration pipelines | One Flow per use case, from raw input to the response schema, composing Gateways, Logics and Adapters. Business logs belong here |
| 7 | Handlers only forward | They pass the transport input to a Flow and return its response schema. Nothing else |
| 8 | Drivers implement Protocols | External libraries live outside the domain code |
| 9 | Side effects at the edges | IO with data conversion (database, external APIs) goes through Gateways. Simple effects (log, randomness, time) are Protocols the Flow calls directly, with values already decided by Logics or built by Adapters |

Naming: contracts are `<Capability>Protocol` (`DatabaseProtocol`, `LoggerProtocol`) and their implementations are `<Technology>Driver` (`SQLiteDriver`, `UUID4Driver`).

More rules:
- **Logs:** each use case writes one structured business event from the Flow: it builds the `LogEntry` with values already decided (level and status come from Logics) and calls `LoggerProtocol` directly, with no Adapter or Gateway in between. Transport logs (route, latency) belong to the Driver.
- **Private functions in a Flow** may only compose layers. They never hold a rule, a conversion or IO of their own.
- **Contract types** (such as `LogEntry`) live with their Protocol, not in Domains.
- **Resources hold configuration only:** values that may change per environment or client without a code change (blocklists, public messages, limits), preferably as JSON/YAML files (12-Factor, factor III). Queries, schemas and decision tables are code: they live next to whoever uses them (Locality of Behavior). SQL goes in the Gateway that runs it, decision tables in the Logic that decides, and DDL in `migrations/`.

## Directory structure

```
project-root/
├── src/
│   ├── protocols/   # infrastructure contracts (typing.Protocol)
│   ├── domains/     # entities and value objects (Pydantic)
│   ├── resources/   # configuration: settings and JSON/YAML files
│   ├── logics/      # pure domain functions
│   ├── adapters/    # data transformations between layers
│   ├── gateways/    # IO through Protocols
│   ├── flows/       # use-case pipelines, organized by domain
│   ├── handlers/    # entry points (HTTP, Kafka, cron, agent tools)
│   └── main.py      # composition root
├── drivers/         # library implementations, outside src/
├── migrations/      # database schema (.sql), applied by the database Driver
└── tests/
    ├── unit/        # Adapters and Logics
    └── integration/ # Flows with in-memory Protocols
```

## Dependency rules

| Layer | May call |
|---|---|
| Protocols, Domains, Resources | nothing |
| Logics | Domains, Resources |
| Adapters | Domains, Resources |
| Gateways | Protocols (IO with data conversion), Domains, Adapters, Resources |
| Flows | Gateways, Logics, Adapters, Protocols, Resources |
| Handlers | Flows, Protocols |
| Drivers | Protocols, Resources |
| `main.py` | Drivers, Handlers, Resources |

```
Request  → Driver → Handler → Flow → Adapter / Logic / Gateway → Protocol (IO)
Response ← Driver ← Handler ← Flow (response schema)
```

## Example: a use case as a Flow

```python
# src/flows/user/create_user_flow.py
def create_user_flow(db, ids, logger, raw: dict) -> CreateUserResponse:
    result = to_create_user_input(raw).bind(                                     # Adapter
        lambda data: flow(
            to_rule_result(check_email_domain(data.email)),                      # Logic + Adapter
            bind(lambda _: find_users_by_email(db, data.email)),                 # Gateway (IO)
            bind(lambda existing: to_rule_result(check_user_is_new(existing))),  # Logic + Adapter
            map_(lambda _: to_user_domain(data, ids.new_id())),                  # Protocol (randomness) + Adapter
            map_(to_user_record),                                                # Adapter
            bind(lambda record: persist_user(db, record)),                       # Gateway (IO)
            map_(to_create_user_output),                                         # Adapter
        )
    )
    outcome = to_create_user_outcome(result)                                     # Adapter: Result -> schema, once
    status = resolve_create_user_status(outcome)                                 # Logic
    logger.log(LogEntry(                                                         # Protocol (IO)
        level=resolve_create_user_log_level(outcome),                            # Logic
        message="create user",
        context={"status": status, "error": outcome.error},
    ))
    return to_create_user_response(status, outcome)                              # Adapter
```

The Flow depends only on Protocols. Even the user id comes from `IdGeneratorProtocol`: generating it is not IO, so the Flow calls it directly and hands the value to the Adapter. Every Adapter and Logic stays pure and tests are deterministic. The [runnable example](examples/user-service) injects SQLite and UUIDv4 Drivers; tests inject an in-memory database and a fixed id.

The Handler only forwards: the Flow owns the whole use case, including the business log and the response schema. A Gateway that would only pass a call through (like writing a log or generating an id) is not created. Logics never build a `Result`; they return decisions as schemas, and an Adapter turns them into pipeline steps. At the end, the `Result` becomes an outcome schema once, and the log and response Adapters work on that schema.

```python
# src/logics/user_logic.py: decisions as data, never Result
def check_user_is_new(existing: list[UserRecord]) -> UserRuleCheck:
    if existing:
        return UserRuleCheck(error=UserError.USER_ALREADY_EXISTS)
    return UserRuleCheck()

# src/adapters/user_adapter.py: the bridge from schema to Result
def to_rule_result(check: UserRuleCheck) -> Result[None, UserError]:
    return Maybe.from_optional(check.error).map(Failure).value_or(Success(None))
```

```python
# src/handlers/user_handlers.py: only forwards
def handle_create_user(db, ids, logger, raw_body: dict) -> CreateUserResponse:
    return create_user_flow(db, ids, logger, raw_body)
```

```python
# src/main.py
def create_app() -> FastAPIDriver:
    settings = load_settings()
    db, ids, logger, http = SQLiteDriver(settings), UUID4Driver(), StdoutLoggerDriver(), FastAPIDriver()
    register_user_handlers(http, db, ids, logger)
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

Input Adapters follow the **Tolerant Reader** pattern: they ignore fields they do not need, so upstream services can add fields without breaking consumers. Required fields are never defaulted: if one is missing, the input is invalid. External contracts can be declared in `resources/` and checked in CI.

## How TAG compares

| | TAG | Hexagonal | Clean Architecture | DOMA | Diplomat |
|---|---|---|---|---|---|
| Paradigm | Functional | Agnostic | OOP | Agnostic | Functional (Clojure) |
| Scope | Service + organization | Service | Service | Organization | Service |
| Error handling | Result | — | — | — | — |
| Dependency injection | Protocols | Ports | Interfaces | — | Components |

## FAQ

<details><summary><strong>Does it work with any HTTP framework?</strong></summary>

Yes. The framework is a Driver behind the `HttpServerProtocol`. FastAPI, Flask or Starlette can be swapped in `main.py`.
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
