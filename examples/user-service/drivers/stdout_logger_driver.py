import json
import sys

from src.protocols.logger import LogEntry


class StdoutLoggerDriver:
    """Implements the LoggerProtocol with JSON lines on stdout."""

    def log(self, entry: LogEntry) -> None:
        line = {"level": entry["level"], "message": entry["message"], **entry["context"]}
        print(json.dumps(line, default=str), file=sys.stdout)
