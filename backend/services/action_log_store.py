from __future__ import annotations

import sqlite3
from pathlib import Path
from threading import Lock
from datetime import datetime, timezone
from typing import Any, Optional
import json
from contextlib import closing


class ActionLogStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self._lock = Lock()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._lock, closing(self._connect()) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS action_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    product_id TEXT,
                    message TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'completed'
                )
                """
            )
            columns = {
                row["name"]
                for row in conn.execute("PRAGMA table_info(action_logs)").fetchall()
            }
            if "status" not in columns:
                conn.execute(
                    "ALTER TABLE action_logs ADD COLUMN status TEXT NOT NULL DEFAULT 'completed'"
                )
            conn.commit()

    def create(
        self,
        action_type: str,
        message: str,
        product_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
        status: str = "completed",
    ) -> dict[str, Any]:
        payload = json.dumps(metadata or {}, ensure_ascii=False)
        now = datetime.now(timezone.utc).isoformat()
        normalized_status = str(status or "completed").strip().lower()
        if normalized_status not in {"pending", "sent", "failed", "completed"}:
            normalized_status = "completed"
        with self._lock, closing(self._connect()) as conn:
            cur = conn.execute(
                """
                INSERT INTO action_logs (timestamp, action_type, product_id, message, metadata, status)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (now, action_type, product_id, message, payload, normalized_status),
            )
            conn.commit()
            row_id = cur.lastrowid
        return self.get_by_id(row_id)

    def update_status(self, row_id: int, status: str) -> dict[str, Any]:
        normalized_status = str(status or "").strip().lower()
        if normalized_status not in {"pending", "sent", "failed", "completed"}:
            raise ValueError("Invalid status value")
        with self._lock, closing(self._connect()) as conn:
            conn.execute(
                "UPDATE action_logs SET status = ? WHERE id = ?",
                (normalized_status, row_id),
            )
            conn.commit()
        return self.get_by_id(row_id)

    def get_by_id(self, row_id: int) -> dict[str, Any]:
        with self._lock, closing(self._connect()) as conn:
            row = conn.execute("SELECT * FROM action_logs WHERE id = ?", (row_id,)).fetchone()
        if row is None:
            raise ValueError(f"Action log not found: {row_id}")
        return self._row_to_dict(row)

    def list(self, limit: int = 50) -> list[dict[str, Any]]:
        safe_limit = max(1, min(limit, 200))
        with self._lock, closing(self._connect()) as conn:
            rows = conn.execute(
                "SELECT * FROM action_logs ORDER BY id DESC LIMIT ?",
                (safe_limit,),
            ).fetchall()
        # Return oldest -> newest for easier reading.
        return [self._row_to_dict(row) for row in reversed(rows)]

    def count(self) -> int:
        with self._lock, closing(self._connect()) as conn:
            row = conn.execute("SELECT COUNT(*) AS c FROM action_logs").fetchone()
        return int(row["c"]) if row else 0

    @staticmethod
    def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
        try:
            metadata = json.loads(row["metadata"] or "{}")
        except json.JSONDecodeError:
            metadata = {}
        return {
            "id": row["id"],
            "timestamp": row["timestamp"],
            "action_type": row["action_type"],
            "product_id": row["product_id"],
            "message": row["message"],
            "metadata": metadata,
            "status": row["status"] or "completed",
        }
