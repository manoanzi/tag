from typing import Any, Literal, Protocol, TypedDict


class LogEntry(TypedDict):
    """What the LoggerProtocol accepts: part of the contract, not of the domain."""

    level: Literal["info", "error"]
    message: str
    context: dict[str, Any]


class LoggerProtocol(Protocol):
    def log(self, entry: LogEntry) -> None: ...
