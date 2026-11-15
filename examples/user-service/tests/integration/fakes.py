from typing import Any
from uuid import UUID

from returns.result import Failure, ResultE, Success

from src.protocols.logger import LogEntry


class FakeDatabase:
    """In-memory implementation of the DatabaseProtocol."""

    def __init__(self, fail: bool = False) -> None:
        self.rows: list[dict[str, Any]] = []
        self.fail = fail

    def execute(self, query: str, params: dict[str, Any]) -> ResultE[list[dict[str, Any]]]:
        if self.fail:
            return Failure(RuntimeError("database unavailable"))
        if "SELECT" in query:
            return Success([row for row in self.rows if row["email"] == params["email"]])
        if "INSERT" in query:
            self.rows.append(params)
            return Success([params])
        return Failure(RuntimeError(f"unsupported query: {query}"))


class FixedIdGenerator:
    """Deterministic implementation of the IdGeneratorProtocol."""

    def __init__(self, value: UUID) -> None:
        self.value = value

    def new_id(self) -> UUID:
        return self.value


class FakeLogger:
    """In-memory implementation of the LoggerProtocol."""

    def __init__(self) -> None:
        self.entries: list[LogEntry] = []

    def log(self, entry: LogEntry) -> None:
        self.entries.append(entry)
