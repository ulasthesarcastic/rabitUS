"""Database connector — reads from and writes to SQL databases."""

from typing import Any

from sqlalchemy import create_engine, text

from backend.models.connection import Connection


class DBConnector:
    def __init__(self, connection: Connection):
        self.connection = connection
        self.engine = self._create_engine()

    def _create_engine(self):
        c = self.connection
        db_type = (c.db_type or "postgresql").lower()
        driver_map = {
            "postgresql": "postgresql",
            "mysql": "mysql+pymysql",
            "mssql": "mssql+pymssql",
        }
        driver = driver_map.get(db_type, db_type)
        url = f"{driver}://{c.db_user}:{c.db_password}@{c.db_host}:{c.db_port}/{c.db_name}"
        return create_engine(url)

    def fetch(self, table: str) -> list[dict[str, Any]]:
        """Read all rows from a table."""
        with self.engine.connect() as conn:
            result = conn.execute(text(f"SELECT * FROM {table}"))  # noqa: S608
            columns = list(result.keys())
            return [dict(zip(columns, row)) for row in result.fetchall()]

    def push(self, table: str, records: list[dict[str, Any]]) -> int:
        """Insert records into a table. Returns number of rows inserted."""
        if not records:
            return 0
        columns = list(records[0].keys())
        col_list = ", ".join(columns)
        param_list = ", ".join(f":{c}" for c in columns)
        stmt = text(f"INSERT INTO {table} ({col_list}) VALUES ({param_list})")  # noqa: S608
        with self.engine.begin() as conn:
            conn.execute(stmt, records)
        return len(records)
