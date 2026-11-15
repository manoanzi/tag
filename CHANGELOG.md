# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Python project template
- Example: complete Payment Service

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

[Unreleased]: https://github.com/manoanzi/tag/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/manoanzi/tag/compare/v0.1.2...v0.2.0
[0.1.2]: https://github.com/manoanzi/tag/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/manoanzi/tag/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/manoanzi/tag/releases/tag/v0.1.0
[0.0.1]: https://github.com/manoanzi/tag/releases/tag/v0.0.1
