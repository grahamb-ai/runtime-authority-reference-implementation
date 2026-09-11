from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from pathlib import Path

from .models import ProtectedClinicalBind


class BindStore:
    def __init__(self, db_path: str | Path):
        self.db_path = str(db_path)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10, isolation_level=None)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS protected_bind ("
                "bind_id TEXT PRIMARY KEY, payload TEXT NOT NULL, status TEXT NOT NULL, updated_at TEXT NOT NULL)"
            )

    def issue(self, bind: ProtectedClinicalBind) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO protected_bind(bind_id,payload,status,updated_at) VALUES (?,?,?,?)",
                (bind.bind_id, json.dumps(asdict(bind), sort_keys=True), "ISSUED", bind.issued_at),
            )

    def get(self, bind_id: str) -> tuple[ProtectedClinicalBind, str] | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT payload,status FROM protected_bind WHERE bind_id=?", (bind_id,)
            ).fetchone()
        if row is None:
            return None
        return ProtectedClinicalBind(**json.loads(row["payload"])), row["status"]

    def claim(self, bind_id: str, now_iso: str) -> bool:
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            cur = conn.execute(
                "UPDATE protected_bind SET status='CLAIMED', updated_at=? "
                "WHERE bind_id=? AND status='ISSUED'",
                (now_iso, bind_id),
            )
            if cur.rowcount != 1:
                conn.execute("ROLLBACK")
                return False
            conn.execute("COMMIT")
            return True
        except Exception:
            try:
                conn.execute("ROLLBACK")
            except Exception:
                pass
            raise
        finally:
            conn.close()

    def set_status(self, bind_id: str, status: str, now_iso: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE protected_bind SET status=?, updated_at=? WHERE bind_id=?",
                (status, now_iso, bind_id),
            )
