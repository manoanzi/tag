import sqlite3
from typing import Any

from returns.result import ResultE, safe

from src.resources.settings import Settings
from src.resources.user_queries import CREATE_USERS_TABLE


class SQLiteDriver:
    """Implements the DatabaseClient Protocol with the standard-library sqlite3."""

    def __init__(self, settings: Settings) -> None:
        self._conn = sqlite3.connect(settings.database_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute(CREATE_USERS_TABLE)

    def execute(self, query: str, params: dict[str, Any]) -> ResultE[list[dict[str, Any]]]:
        return self._execute(query, params)

    @safe
    def _execute(self, query: str, params: dict[str, Any]) -> list[dict[str, Any]]:
        with self._conn:
            cursor = self._conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
