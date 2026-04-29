from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator

try:
    import oracledb
except ImportError:
    oracledb = None


class DatabaseError(RuntimeError):
    """Application-specific database error."""


class DatabaseClient:
    def __init__(self) -> None:
        self._connection = None
        self.info = ""

    @property
    def driver(self) -> Any:
        return oracledb

    def connect(self, user: str, password: str, dsn: str) -> None:
        if oracledb is None:
            raise DatabaseError(
                "Modul 'oracledb' neni nainstalovany. Spustte: pip install oracledb"
            )

        self.disconnect()
        self._connection = oracledb.connect(user=user, password=password, dsn=dsn)
        self.info = f"{user}@{dsn}"

    def disconnect(self) -> None:
        if self._connection is not None:
            self._connection.close()
        self._connection = None
        self.info = ""

    def is_connected(self) -> bool:
        return self._connection is not None

    def require_connection(self) -> Any:
        if not self.is_connected():
            raise DatabaseError("Nejdriv navazte spojeni s databazi Oracle.")
        return self._connection

    def commit(self) -> None:
        if self.is_connected():
            self._connection.commit()

    def rollback(self) -> None:
        if self.is_connected():
            self._connection.rollback()

    @contextmanager
    def cursor(self) -> Iterator[Any]:
        cursor = self.require_connection().cursor()
        try:
            yield cursor
        finally:
            cursor.close()

    @contextmanager
    def transaction(self) -> Iterator[None]:
        try:
            yield
        except Exception:
            self.rollback()
            raise
        else:
            self.commit()

    def fetch_all(self, sql: str, params: dict[str, Any] | None = None) -> tuple[list[str], list[tuple[Any, ...]]]:
        with self.cursor() as cursor:
            cursor.execute(sql, params or {})
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description or []]
        return columns, rows

    def fetch_one(self, sql: str, params: dict[str, Any] | None = None) -> tuple[list[str], tuple[Any, ...] | None]:
        columns, rows = self.fetch_all(sql, params)
        return columns, rows[0] if rows else None

    def fetch_scalar(self, sql: str, params: dict[str, Any] | None = None, default: Any = None) -> Any:
        _, row = self.fetch_one(sql, params)
        if row is None:
            return default
        return row[0]
