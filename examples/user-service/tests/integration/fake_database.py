from typing import Any

from returns.result import Failure, ResultE, Success


class FakeDatabaseClient:
    """In-memory implementation of the DatabaseClient Protocol."""

    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def execute(self, query: str, params: dict[str, Any]) -> ResultE[list[dict[str, Any]]]:
        if "SELECT" in query:
            return Success([r for r in self.rows if r["email"] == params["email"]])
        if "INSERT" in query:
            self.rows.append(params)
            return Success([])
        return Failure(Exception(f"unsupported query: {query}"))
