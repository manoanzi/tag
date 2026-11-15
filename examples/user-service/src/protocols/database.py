from typing import Any, Protocol

from returns.result import ResultE


class DatabaseClient(Protocol):
    def execute(self, query: str, params: dict[str, Any]) -> ResultE[list[dict[str, Any]]]: ...
