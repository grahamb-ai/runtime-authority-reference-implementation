from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable

from .executor import EPRSimulator
from .models import ExactClinicalCommit
from .runtime import HarnessClock, verify_bind_integrity
from .store import BindStore

EXPECTED_STATE_SOURCE = "HC-STATE-01"
MAX_STANDING_AGE_SECONDS = 30


@dataclass(frozen=True)
class PresentStandingSnapshot:
    source_id: str
    state_epoch: int
    sequence: int
    observed_at: str
    product_authorised: bool = True
    workflow_valid: bool = True
    monitoring_clear: bool = True
    policy_version: str = "HC-POL-1.0"
    available: bool = True

    @property
    def position(self) -> tuple[int, int]:
        return (self.state_epoch, self.sequence)

    @property
    def fingerprint(self) -> str:
        payload = json.dumps(asdict(self), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class MutableStandingProvider:
    """Reference-only authoritative state provider used by HARDEN-002 tests."""

    def __init__(self, snapshot: PresentStandingSnapshot):
        self._lock = threading.Lock()
        self._snapshot = snapshot

    def read(self) -> PresentStandingSnapshot:
        with self._lock:
            return self._snapshot

    def set(self, snapshot: PresentStandingSnapshot) -> None:
        with self._lock:
            self._snapshot = snapshot

    def update(self, **changes) -> PresentStandingSnapshot:
        with self._lock:
            self._snapshot = replace(self._snapshot, **changes)
            return self._snapshot


class StateWatermarkStore:
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
                "CREATE TABLE IF NOT EXISTS standing_watermark ("
                "source_id TEXT PRIMARY KEY, state_epoch INTEGER NOT NULL, sequence INTEGER NOT NULL, "
                "fingerprint TEXT NOT NULL)"
            )

    def get(self, source_id: str) -> tuple[int, int] | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT state_epoch, sequence FROM standing_watermark WHERE source_id=?",
                (source_id,),
            ).fetchone()
        if row is None:
            return None
        return (row["state_epoch"], row["sequence"])

    def accept(self, snapshot: PresentStandingSnapshot) -> str:
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT state_epoch, sequence, fingerprint FROM standing_watermark WHERE source_id=?",
                (snapshot.source_id,),
            ).fetchone()
            if row is not None:
                current = (row["state_epoch"], row["sequence"])
                if snapshot.position < current:
                    conn.execute("ROLLBACK")
                    return "ROLLBACK"
                if snapshot.position == current and snapshot.fingerprint != row["fingerprint"]:
                    conn.execute("ROLLBACK")
                    return "EQUIVOCATION"
            conn.execute(
                "INSERT INTO standing_watermark(source_id,state_epoch,sequence,fingerprint) VALUES (?,?,?,?) "
                "ON CONFLICT(source_id) DO UPDATE SET state_epoch=excluded.state_epoch, "
                "sequence=excluded.sequence, fingerprint=excluded.fingerprint",
                (snapshot.source_id, snapshot.state_epoch, snapshot.sequence, snapshot.fingerprint),
            )
            conn.execute("COMMIT")
            return "ACCEPTED"
        except Exception:
            try:
                conn.execute("ROLLBACK")
            except Exception:
                pass
            raise
        finally:
            conn.close()


class ContinuityProtectedExecutor:
    def __init__(
        self,
        store: BindStore,
        simulator: EPRSimulator,
        clock: HarnessClock,
        standing_provider: MutableStandingProvider,
        watermark_store: StateWatermarkStore,
        before_final_check: Callable[[], None] | None = None,
        expected_source_id: str = EXPECTED_STATE_SOURCE,
        max_standing_age_seconds: int = MAX_STANDING_AGE_SECONDS,
    ):
        self.store = store
        self.simulator = simulator
        self.clock = clock
        self.standing_provider = standing_provider
        self.watermark_store = watermark_store
        self.before_final_check = before_final_check
        self.expected_source_id = expected_source_id
        self.max_standing_age_seconds = max_standing_age_seconds

    def _standing_fresh(self, standing: PresentStandingSnapshot, now: datetime) -> bool:
        observed = datetime.fromisoformat(standing.observed_at)
        if observed > now:
            return False
        return now - observed <= timedelta(seconds=self.max_standing_age_seconds)

    def _standing_valid(self, standing: PresentStandingSnapshot, commit: ExactClinicalCommit) -> bool:
        return (
            standing.available
            and standing.product_authorised
            and standing.workflow_valid
            and standing.monitoring_clear
            and standing.policy_version == commit.runtime_policy_version
        )

    def _accept_standing(self, standing: PresentStandingSnapshot, now: datetime) -> str | None:
        if standing.source_id != self.expected_source_id:
            return "STATE_SOURCE_MISMATCH"
        if not standing.available:
            return "PRESENT_STANDING_UNAVAILABLE"
        if not self._standing_fresh(standing, now):
            return "PRESENT_STANDING_STALE"
        accepted = self.watermark_store.accept(standing)
        if accepted == "ROLLBACK":
            return "STATE_ROLLBACK_DETECTED"
        if accepted == "EQUIVOCATION":
            return "STATE_EQUIVOCATION_DETECTED"
        return None

    def execute(self, bind_id: str, attempted_commit: ExactClinicalCommit) -> str:
        current = self.store.get(bind_id)
        if current is None:
            return "NO_VALID_BIND"
        bind, status = current

        if not verify_bind_integrity(bind):
            return "BIND_INTEGRITY_FAILURE"
        if status != "ISSUED":
            return "BIND_ALREADY_USED"

        now = self.clock.now()
        if now > datetime.fromisoformat(bind.expires_at):
            self.store.set_status(bind.bind_id, "EXPIRED", now.isoformat())
            return "BIND_EXPIRED"

        if bind.materiality_profile != attempted_commit.materiality_profile:
            return "BINDING_MISMATCH"
        if bind.canonicalisation_profile != attempted_commit.canonicalisation_profile:
            return "BINDING_MISMATCH"
        if bind.commit_binding_hash != attempted_commit.commit_binding_hash:
            return "BINDING_MISMATCH"

        first = self.standing_provider.read()
        standing_error = self._accept_standing(first, now)
        if standing_error:
            return standing_error
        if not self._standing_valid(first, attempted_commit):
            return "PRESENT_STANDING_INVALID"

        if not self.store.claim(bind.bind_id, now.isoformat()):
            return "ATOMIC_CLAIM_FAILED"

        if self.before_final_check is not None:
            self.before_final_check()

        final_now = self.clock.now()
        if final_now > datetime.fromisoformat(bind.expires_at):
            self.store.set_status(bind.bind_id, "EXPIRED", final_now.isoformat())
            return "BIND_EXPIRED"

        second = self.standing_provider.read()
        standing_error = self._accept_standing(second, final_now)
        if standing_error:
            self.store.set_status(bind.bind_id, "INVALIDATED", final_now.isoformat())
            return standing_error
        if not self._standing_valid(second, attempted_commit):
            self.store.set_status(bind.bind_id, "INVALIDATED", final_now.isoformat())
            if second.position != first.position or second != first:
                return "PRESENT_STANDING_CHANGED"
            return "PRESENT_STANDING_INVALID"

        try:
            self.simulator.commit(attempted_commit)
            self.store.set_status(bind.bind_id, "CONSUMED", self.clock.now().isoformat())
            return "EXECUTED"
        except Exception:
            self.store.set_status(bind.bind_id, "INDETERMINATE", self.clock.now().isoformat())
            return "EXECUTION_INDETERMINATE"
