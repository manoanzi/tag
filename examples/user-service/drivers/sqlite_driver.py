import sqlite3
from pathlib import Path
from typing import Any

from returns.result import ResultE, safe

from src.resources.settings import Settings

MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "migrations"


class SQLiteDriver:
    """Implements the DatabaseProtocol with the standard-library sqlite3."""

    def __init__(self, settings: Settings) -> None:
        self._conn = sqlite3.connect(settings.database_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        for migration in sorted(MIGRATIONS_DIR.glob("*.sql")):
            self._conn.executescript(migration.read_text())

    def execute(self, query: str, params: dict[str, Any]) -> ResultE[list[dict[str, Any]]]:
        return self._execute(query, params)

    @safe
    def _execute(self, query: str, params: dict[str, Any]) -> list[dict[str, Any]]:
        with self._conn:
            cursor = self._conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
