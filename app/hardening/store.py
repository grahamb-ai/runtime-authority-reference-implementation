from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from pathlib import Path

from .models import ProtectedClinicalBind


class BindStore:
    """Reference persistent store for Protected Clinical Bind state.

    The operational bind database is paired with a separate claim-anchor
    database. The anchor is written before the operational CLAIMED transition,
    so replacement or rollback of the operational database alone cannot
    silently resurrect a previously claimed bind inside the harness boundary.

    This models a stronger failure domain; it is not a production external
    cryptographic anchor or distributed consensus claim.
    """

    def __init__(self, db_path: str | Path, anchor_path: str | Path | None = None):
        path = Path(db_path)
        self.db_path = str(path)
        self.anchor_path = str(anchor_path or (path.parent / f".{path.name}.claim-anchor.sqlite"))
        self._init_db()
        self._init_anchor()

    def _connect(self, path: str | None = None) -> sqlite3.Connection:
        conn = sqlite3.connect(path or self.db_path, timeout=10, isolation_level=None)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect(self.db_path) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS protected_bind ("
                "bind_id TEXT PRIMARY KEY, payload TEXT NOT NULL, status TEXT NOT NULL, updated_at TEXT NOT NULL)"
            )

    def _init_anchor(self) -> None:
        with self._connect(self.anchor_path) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS claimed_bind_anchor ("
                "bind_id TEXT PRIMARY KEY, claimed_at TEXT NOT NULL)"
            )

    def issue(self, bind: ProtectedClinicalBind) -> None:
        with self._connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO protected_bind(bind_id,payload,status,updated_at) VALUES (?,?,?,?)",
                (bind.bind_id, json.dumps(asdict(bind), sort_keys=True), "ISSUED", bind.issued_at),
            )

    def get(self, bind_id: str) -> tuple[ProtectedClinicalBind, str] | None:
        with self._connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT payload,status FROM protected_bind WHERE bind_id=?", (bind_id,)
            ).fetchone()
        if row is None:
            return None
        return ProtectedClinicalBind(**json.loads(row["payload"])), row["status"]

    def _anchor_claim(self, bind_id: str, now_iso: str) -> bool:
        conn = self._connect(self.anchor_path)
        try:
            conn.execute("BEGIN IMMEDIATE")
            cur = conn.execute(
                "INSERT OR IGNORE INTO claimed_bind_anchor(bind_id,claimed_at) VALUES (?,?)",
                (bind_id, now_iso),
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

    def claim(self, bind_id: str, now_iso: str) -> bool:
        # Anchor first. An interrupted update may conservatively burn a bind,
        # but it cannot silently restore execution authority from an older
        # operational database state.
        if not self._anchor_claim(bind_id, now_iso):
            return False

        conn = self._connect(self.db_path)
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
        with self._connect(self.db_path) as conn:
            conn.execute(
                "UPDATE protected_bind SET status=?, updated_at=? WHERE bind_id=?",
                (status, now_iso, bind_id),
            )


class BreakGlassUseStore:
    """Reference durable replay store for single-use break-glass authority.

    Multiple enforcer instances that share this store atomically consume the
    same override identifier. This demonstrates cross-instance and restart
    replay resistance inside one SQLite-backed failure domain only. It is not a
    production distributed consensus or external monotonic-anchor claim.
    """

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
                "CREATE TABLE IF NOT EXISTS consumed_break_glass ("
                "override_id TEXT PRIMARY KEY, consumed_at TEXT NOT NULL)"
            )

    def consume(self, override_id: str, now_iso: str) -> bool:
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            cur = conn.execute(
                "INSERT OR IGNORE INTO consumed_break_glass(override_id,consumed_at) VALUES (?,?)",
                (override_id, now_iso),
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
