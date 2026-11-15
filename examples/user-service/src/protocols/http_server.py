from typing import Any, Callable, Protocol


class HttpResponseProtocol(Protocol):
    """Any response schema with a status code and a JSON-ready body."""

    @property
    def status(self) -> int: ...

    @property
    def body(self) -> dict[str, Any]: ...


Handler = Callable[[dict[str, Any]], HttpResponseProtocol]


class HttpServerProtocol(Protocol):
    def post(self, path: str, handler: Handler) -> None: ...
