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
| Protocols | `src/protocols/` | `DatabaseProtocol`, `HttpServerProtocol`, `LoggerProtocol` (+ `LogEntry`), `IdGeneratorProtocol` |
| Domains | `src/domains/user.py` | Immutable schemas: `User`, `UserRecord`, `UserRuleCheck`, `CreateUserOutcome`, `CreateUserResponse`, `UserError` |
| Resources | `src/resources/` | Settings, SQL queries and JSON config: blocked e-mail domains, HTTP status per outcome, error messages |
| Logics | `src/logics/user_logic.py` | Every decision, returned as a schema: blocked domains, duplicates, HTTP status. No `Result` |
| Adapters | `src/adapters/user_adapter.py` | Pure conversions: input, domain, record, query params, rows, errors, rule checks to `Result`, log entry, response |
| Gateways | `src/gateways/` | The only callers of Protocols: database, id generator and log |
| Flows | `src/flows/user/create_user_flow.py` | The whole use case: raw input to `CreateUserResponse`, including the business log |
| Handlers | `src/handlers/user_handlers.py` | Only forward the request body to the Flow |
| Drivers | `drivers/` | FastAPI, SQLite, UUIDv4 and stdout logger implementations |
| Composition | `src/main.py` | The only place that instantiates Drivers |

## Tests

| Type | Folder | Infrastructure |
|---|---|---|
| Unit | `tests/unit/` | None (pure functions) |
| Integration | `tests/integration/` | Full Flow with in-memory database, logger and a fixed id |
| HTTP | `tests/e2e/` | FastAPI `TestClient` with in-memory SQLite |

Swapping SQLite for Postgres, or UUIDv4 for UUIDv7, means writing a new Driver and changing one line in `src/main.py`. No Flow, Logic, Adapter or Gateway changes.
