# Contributing to TAG

🇧🇷 [Leia em português](CONTRIBUTING.pt-BR.md)

Thanks for considering a contribution to TAG. This document describes how to contribute.

## How to contribute

1. **Fork the repository**
   ```bash
   git clone https://github.com/manoanzi/tag.git
   cd tag
   ```

2. **Create a branch**
   ```bash
   git checkout -b feature/my-contribution
   ```

3. **Make your changes**
   - Follow the TAG principles strictly
   - Add tests for new examples
   - Use type hints on every function

4. **Run the example tests**
   ```bash
   cd examples/user-service
   pip install -e ".[dev]"
   pytest
   ```

5. **Commit your changes**
   ```bash
   git commit -m "Add: short description of the contribution"
   ```

6. **Push your branch**
   ```bash
   git push origin feature/my-contribution
   ```

7. **Open a Pull Request**
   - Describe clearly what changed
   - Reference related issues
   - Wait for review; CI must be green

## Contribution areas

- Practical Python examples
- Advanced testing patterns
- Documentation improvements
- Templates and project-structure tooling
- Tutorials and guides

## Code guidelines

- Python 3.11+
- Follow PEP 8
- Type hints on every function and return value
- Functional, immutable code
- `snake_case` for every file and module

## TAG principles

Every contribution must follow the 9 core principles:

1. **Protocols define contracts**: infrastructure abstractions through `typing.Protocol`
2. **Domains are schemas, never functions**: immutable Pydantic entities
3. **Logics are pure**: no IO, data in and data out
4. **Adapters transform structures**: conversions between layers with no side effects
5. **Gateways do IO**: external access through Protocols received as parameters
6. **Flows are orchestration pipelines**: they compose Gateways, Logics and Adapters
7. **Handlers connect transport to Flows**: they own a request's lifecycle, from input to output
8. **Drivers implement Protocols**: they wrap external libraries outside `src/`
9. **IO at the edges**: side effects live only in Gateways and Drivers

## Review process

1. A maintainer reviews the PR
2. Discussion and adjustments if needed
3. Approval and merge
4. CHANGELOG update

## Code of Conduct

This project follows the [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold it.

## Questions?

Open an [issue](https://github.com/manoanzi/tag/issues) to start a discussion.

---

**Thanks for contributing to TAG.**
