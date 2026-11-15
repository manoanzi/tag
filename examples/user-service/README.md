# TAG example: user service

A runnable service built with the TAG layers: a `POST /users` endpoint that validates, checks for duplicates and stores a user.
It uses FastAPI and SQLite, so it runs with no external infrastructure.

🇧🇷 Um serviço executável com as camadas do TAG: `POST /users` valida, verifica duplicidade e grava o usuário. Usa FastAPI e SQLite, sem infraestrutura externa.

## Run

```bash
cd examples/user-service
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

pytest                 # unit, integration and HTTP tests
python -m src.main     # http://localhost:8000/docs
```

```bash
curl -X POST localhost:8000/users -H 'content-type: application/json' \
  -d '{"email": "ana@gmail.com", "name": "Ana"}'
# 201 {"id": "...", "email": "ana@gmail.com", "name": "Ana"}
# same request again           → 409 {"error": "user_already_exists", "message": "A user with this email already exists"}
# {"email": "x@tempmail.com"}  → 422 {"error": "email_domain_not_allowed", ...}
# {"email": "nope"}            → 422 {"error": "invalid_payload", ...}
```

## Where things live

| Layer | File | Role |
|---|---|---|
| Protocols | `src/protocols/` | `DatabaseProtocol`, `HttpServerProtocol`, `LoggerProtocol`, `IdGeneratorProtocol` |
| Domains | `src/domains/user.py` | Immutable schemas, including `UserRecord` and the `UserError` enum |
| Resources | `src/resources/` | Settings and SQL queries |
| Logics | `src/logics/user_logic.py` | Every decision: blocked domains, duplicates, HTTP status per error |
| Adapters | `src/adapters/user_adapter.py` | Pure conversions: input, domain, record, query params, rows, errors, response body |
| Gateways | `src/gateways/user_gateway.py` | IO and randomness through `DatabaseProtocol` and `IdGeneratorProtocol` |
| Flows | `src/flows/user/create_user_flow.py` | The use case as a `Result` pipeline |
| Handlers | `src/handlers/user_handlers.py` | Chains Adapter → Flow → Logic, with no `if` or `match` |
| Drivers | `drivers/` | FastAPI, SQLite, UUIDv4 and stdout logger implementations |
| Composition | `src/main.py` | The only place that instantiates Drivers |

## Tests

| Type | Folder | Infrastructure |
|---|---|---|
| Unit | `tests/unit/` | None (pure functions) |
| Integration | `tests/integration/` | In-memory `DatabaseProtocol` and a fixed `IdGeneratorProtocol` |
| HTTP | `tests/e2e/` | FastAPI `TestClient` with in-memory SQLite |

Swapping SQLite for Postgres, or UUIDv4 for UUIDv7, means writing a new Driver and changing one line in `src/main.py`. No Flow, Logic, Adapter or Gateway changes.
