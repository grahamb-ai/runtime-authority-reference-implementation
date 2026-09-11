from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class AuthorityState:
    service_id: str
    epoch: int
    sequence: int
    state_payload: str

    @property
    def position(self) -> tuple[int, int]:
        return (self.epoch, self.sequence)

    @property
    def fingerprint(self) -> str:
        raw = json.dumps({"epoch": self.epoch, "sequence": self.sequence, "state_payload": self.state_payload}, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class AuthorityTrustProfile:
    profile_id: str
    profile_version: int
    deployment_id: str
    authorised_service_ids: tuple[str, ...]
    independence_level: int


@dataclass(frozen=True)
class RecoveryEvidence:
    status: str
    reason: str
    service_id: str
    profile_id: str
    profile_version: int
    observed_epoch: int | None
    observed_sequence: int | None
    accepted_epoch: int | None
    accepted_sequence: int | None
    fingerprint: str | None
    independence_level: int


class RecoveryWatermarkStore:
    def __init__(self, db_path: str | Path):
        self.db_path = str(db_path)
        self._init_db()

    def _connect(self):
        conn = sqlite3.connect(self.db_path, timeout=10, isolation_level=None)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._connect() as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS recovery_watermark (deployment_id TEXT PRIMARY KEY, epoch INTEGER NOT NULL, sequence INTEGER NOT NULL, fingerprint TEXT NOT NULL)")

    def read(self, deployment_id: str):
        with self._connect() as conn:
            row = conn.execute("SELECT epoch, sequence, fingerprint FROM recovery_watermark WHERE deployment_id=?", (deployment_id,)).fetchone()
        if row is None:
            return None
        return (row["epoch"], row["sequence"], row["fingerprint"])

    def accept(self, deployment_id: str, state: AuthorityState) -> str:
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute("SELECT epoch, sequence, fingerprint FROM recovery_watermark WHERE deployment_id=?", (deployment_id,)).fetchone()
            if row:
                current = (row["epoch"], row["sequence"])
                if state.position < current:
                    conn.execute("ROLLBACK")
                    return "ROLLBACK"
                if state.position == current and state.fingerprint != row["fingerprint"]:
                    conn.execute("ROLLBACK")
                    return "EQUIVOCATION"
            conn.execute("INSERT INTO recovery_watermark(deployment_id,epoch,sequence,fingerprint) VALUES (?,?,?,?) ON CONFLICT(deployment_id) DO UPDATE SET epoch=excluded.epoch, sequence=excluded.sequence, fingerprint=excluded.fingerprint", (deployment_id, state.epoch, state.sequence, state.fingerprint))
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


class RecoveryAuthorityGate:
    def __init__(self, active_profile: AuthorityTrustProfile, store: RecoveryWatermarkStore, requester_service_id: str = "REQUESTING_AI"):
        self.active_profile = active_profile
        self.store = store
        self.requester_service_id = requester_service_id

    def evaluate(self, supplied_profile: AuthorityTrustProfile, state: AuthorityState) -> RecoveryEvidence:
        accepted = self.store.read(self.active_profile.deployment_id)
        accepted_epoch = accepted[0] if accepted else None
        accepted_sequence = accepted[1] if accepted else None

        def result(status: str, reason: str) -> RecoveryEvidence:
            return RecoveryEvidence(status, reason, state.service_id, supplied_profile.profile_id, supplied_profile.profile_version, state.epoch, state.sequence, accepted_epoch, accepted_sequence, state.fingerprint, supplied_profile.independence_level)

        if supplied_profile != self.active_profile:
            return result("PREVENTED", "trust profile is not exact active profile")
        if state.service_id == self.requester_service_id:
            return result("PREVENTED", "requesting service cannot become runtime authority")
        if state.service_id not in self.active_profile.authorised_service_ids:
            return result("PREVENTED", "authority service identity not authorised")
        if not isinstance(state.epoch, int) or not isinstance(state.sequence, int) or state.epoch < 0 or state.sequence < 0:
            return result("PREVENTED", "invalid authority position")
        try:
            decision = self.store.accept(self.active_profile.deployment_id, state)
        except Exception:
            return result("INDETERMINATE", "persistent authority high-watermark unavailable")
        if decision == "ROLLBACK":
            return result("PREVENTED", "recovery state behind accepted high-watermark")
        if decision == "EQUIVOCATION":
            return result("PREVENTED", "same authority position has different state fingerprint")
        return result("ACTIVE", "authority state accepted")
