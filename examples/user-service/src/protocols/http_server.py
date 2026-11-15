from typing import Any, Callable, Protocol

Handler = Callable[[dict[str, Any]], tuple[int, dict[str, Any]]]


class HttpServerProtocol(Protocol):
    def post(self, path: str, handler: Handler) -> None: ...
