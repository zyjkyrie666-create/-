from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from dataclasses import asdict
from pathlib import Path

from industrial_agent.domain.models import AgentRun


class SQLiteRunRepository:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_schema(self) -> None:
        with closing(self._connect()) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS agent_runs (
                    id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    query TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def save(self, run: AgentRun) -> None:
        payload = json.dumps(_to_jsonable(asdict(run)), ensure_ascii=False)
        with closing(self._connect()) as conn:
            conn.execute(
                """
                INSERT INTO agent_runs (id, status, user_id, query, payload, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    status = excluded.status,
                    payload = excluded.payload,
                    updated_at = excluded.updated_at
                """,
                (
                    run.id,
                    run.status.value,
                    run.request.user_id,
                    run.request.query,
                    payload,
                    run.created_at.isoformat(),
                    run.updated_at.isoformat(),
                ),
            )
            conn.commit()

    def get_payload(self, run_id: str) -> dict | None:
        with closing(self._connect()) as conn:
            row = conn.execute("SELECT payload FROM agent_runs WHERE id = ?", (run_id,)).fetchone()
        if row is None:
            return None
        return json.loads(row[0])


def _to_jsonable(value):
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if hasattr(value, "value"):
        return value.value
    if isinstance(value, dict):
        return {key: _to_jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_to_jsonable(item) for item in value]
    return value
