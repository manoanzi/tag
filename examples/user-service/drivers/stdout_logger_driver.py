import json
import sys
from typing import Any


class StdoutLoggerDriver:
    """Implements the Logger Protocol with JSON lines on stdout."""

    def info(self, message: str, **context: Any) -> None:
        self._write("info", message, context)

    def error(self, message: str, **context: Any) -> None:
        self._write("error", message, context)

    def _write(self, level: str, message: str, context: dict[str, Any]) -> None:
        print(json.dumps({"level": level, "message": message, **context}, default=str), file=sys.stdout)
