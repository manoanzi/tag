# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Python project template
- Example: complete Payment Service

## [0.3.5] - 2026-11-15

### Changed
- `to_rule_result` became the Logic `enforce_rule`, and `to_single_user_record` became the Logic `require_written_record`, called by the Flow: choosing a path (continue or fail) is a decision, not a reshape
- `persist_user` returns the written records; the Flow decides and converts them
- Documented test: a function that chooses a path or picks a value by a rule is a Logic; one that only reshapes data is an Adapter

## [0.3.4] - 2026-11-15

### Changed
- The Flow builds a single structured `LogEntry` per use case (`create user`, with status and error) and calls `LoggerProtocol` directly
- Log level is a Logic decision (`resolve_create_user_log_level`); the `to_create_user_log_entry` Adapter and the `write_log` Gateway were removed
- Rule clarified: Gateways are for IO with data conversion; simple effects (log, randomness, time) are called by the Flow with values already decided

## [0.3.3] - 2026-11-15

### Fixed
- Tolerant Reader no longer defaults missing fields: a request without `name` (or with an empty one) is now `invalid_payload` (422) instead of creating a user with an empty name
- A write that returns no row is a `storage_failure` instead of an `IndexError` escaping the `Result` pipeline

### Changed
- The `Result` becomes `CreateUserOutcome` once in the Flow; the log and response Adapters work on that schema, removing three repeated `map`/`lash`/`unwrap` chains
- Rows always go through `UserRecord` before the domain (`to_user_records` -> `to_single_user_record` -> `to_user_from_record`)
- `to_query_params` renamed to `to_user_query_params`; the private parsing helper was replaced by `safe(CreateUserInput.model_validate)`

## [0.3.2] - 2026-11-15

### Changed
- The Flow calls `IdGeneratorProtocol` directly and passes the id to the Adapter: generating an id is not IO, so the `generate_user_id` Gateway was removed
- Rule clarified: Gateways are the only layer that does IO through Protocols; randomness and time Protocols are called by the Flow

## [0.3.1] - 2026-11-15

### Changed
- SQL queries live inline in the Gateway that runs them (Locality of Behavior)
- Database schema moved to `migrations/001_create_users.sql`, applied in order by `SQLiteDriver`
- HTTP status per outcome is a decision table in the Logic again: it never changes between environments
- Resources documented as configuration only (12-Factor, factor III): blocked domains and public error messages

## [0.3.0] - 2026-11-15

### Changed
- **BREAKING:** Handlers only forward the request to a Flow and return its response schema (`CreateUserResponse`), never a tuple
- **BREAKING:** `LoggerProtocol` has a single `log(entry: LogEntry)` method; `LogEntry` is part of the Protocol contract, not of the domain
- Flows own the whole use case: they start from the raw input and write the business log through an Adapter and the `write_log` Gateway
- Logics never build `Result`: decisions come back as schemas (`UserRuleCheck`, `CreateUserOutcome`) and Adapters turn them into pipeline steps
- Static data (blocked e-mail domains, HTTP status per outcome, error messages) moved to JSON files in Resources; `UserError` values are now codes
- Documented rules: transport logs belong to Drivers, and private functions in a Flow may only compose layers

## [0.2.0] - 2026-11-15

### Changed
- **BREAKING:** Protocols are named `<Capability>Protocol` (`DatabaseProtocol`, `HttpServerProtocol`, `LoggerProtocol`)
- **BREAKING:** Handlers may call Logics; they chain Adapter → Flow → Logic with no `if` or `match`
- Decisions live in Logics, including the HTTP status for each `UserError`
- Adapters own every conversion: `UserRecord`, query params (`model_dump`), rows back to the domain, storage errors and the response body
- Randomness is a side effect: user ids come from `IdGeneratorProtocol` (`UUID4Driver`), so Adapters stay pure and tests are deterministic
- Typed `UserError` enum replaces string errors; duplicate e-mail now returns 409 and validation errors return 422

## [0.1.2] - 2026-11-15

### Added
- GitHub Actions CI running the example tests on Python 3.11, 3.12 and 3.13
- English `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md` (Portuguese versions kept as `*.pt-BR.md`)

### Changed
- CHANGELOG in English
- Example dev dependencies include `httpx2`, which removes the Starlette `TestClient` deprecation warning

## [0.1.1] - 2026-11-15

### Fixed
- Dependency rules: Gateways may use Resources (queries), as the example already did
- Input Adapter returns `Result` (`@safe`) instead of raising a validation exception
- README code snippet aligned with the runnable example
- LICENSE year and holder; contact in the Code of Conduct

## [0.1.0] - 2026-11-15

### Added
- Runnable example `examples/user-service` (FastAPI + SQLite) using every TAG layer
- Unit, integration and HTTP tests in the example
- README in English (`README.md`) and Portuguese (`README.pt-BR.md`)

## [0.0.1] - 2026-01-21

### Added
- Initial documentation of the TAG architecture
- Full specification of the 9 layers
- Python 3.11+ examples
- Core principles and philosophy
- Comparison with other architectures (Hexagonal, Clean, DOMA)
- Recommended Python stack
- Unit and integration testing guide
- FAQ
- MIT license
- GitHub governance files

### Philosophy
- Functional programming
- Domain orientation
- Railway-oriented programming
- Handlers without business logic
- Protocol-based dependency injection

[Unreleased]: https://github.com/manoanzi/tag/compare/v0.3.5...HEAD
[0.3.5]: https://github.com/manoanzi/tag/compare/v0.3.4...v0.3.5
[0.3.4]: https://github.com/manoanzi/tag/compare/v0.3.3...v0.3.4
[0.3.3]: https://github.com/manoanzi/tag/compare/v0.3.2...v0.3.3
[0.3.2]: https://github.com/manoanzi/tag/compare/v0.3.1...v0.3.2
[0.3.1]: https://github.com/manoanzi/tag/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/manoanzi/tag/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/manoanzi/tag/compare/v0.1.2...v0.2.0
[0.1.2]: https://github.com/manoanzi/tag/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/manoanzi/tag/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/manoanzi/tag/releases/tag/v0.1.0
[0.0.1]: https://github.com/manoanzi/tag/releases/tag/v0.0.1
