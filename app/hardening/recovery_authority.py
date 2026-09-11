from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path

MAX_DEMONSTRATED_INDEPENDENCE_LEVEL = 2


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
        raw = json.dumps(
            {"epoch": self.epoch, "sequence": self.sequence, "state_payload": self.state_payload},
            sort_keys=True,
            separators=(",", ":"),
        )
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
    """Reference-only dual persistence for recovery high-watermark state.

    The operational recovery database and an anchor database are deliberately
    separate files. The anchor path defaults to a stable sibling file so that
    replacement of the local recovery DB does not reset accepted authority
    standing inside the harness boundary. This models an external anchor; it
    is not a production isolation or consensus claim.
    """

    def __init__(self, db_path: str | Path, anchor_path: str | Path | None = None):
        path = Path(db_path)
        self.db_path = str(path)
        self.anchor_path = str(anchor_path or (path.parent / ".recovery_authority_anchor.db"))
        self._init_db(self.db_path)
        self._init_db(self.anchor_path)

    def _connect(self, path: str):
        conn = sqlite3.connect(path, timeout=10, isolation_level=None)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self, path: str):
        with self._connect(path) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS recovery_watermark ("
                "deployment_id TEXT PRIMARY KEY, epoch INTEGER NOT NULL, sequence INTEGER NOT NULL, fingerprint TEXT NOT NULL)"
            )

    def _read_one(self, path: str, deployment_id: str):
        with self._connect(path) as conn:
            row = conn.execute(
                "SELECT epoch, sequence, fingerprint FROM recovery_watermark WHERE deployment_id=?",
                (deployment_id,),
            ).fetchone()
        if row is None:
            return None
        return (row["epoch"], row["sequence"], row["fingerprint"])

    def read(self, deployment_id: str):
        local = self._read_one(self.db_path, deployment_id)
        anchor = self._read_one(self.anchor_path, deployment_id)
        if local is None:
            return anchor
        if anchor is None:
            return local
        local_pos = local[:2]
        anchor_pos = anchor[:2]
        if local_pos > anchor_pos:
            return local
        if anchor_pos > local_pos:
            return anchor
        if local[2] != anchor[2]:
            raise RuntimeError("local/anchor authority high-watermark equivocation")
        return local

    def _compare(self, current, state: AuthorityState) -> str | None:
        if current is None:
            return None
        current_pos = current[:2]
        if state.position < current_pos:
            return "ROLLBACK"
        if state.position == current_pos and state.fingerprint != current[2]:
            return "EQUIVOCATION"
        return None

    def _write(self, path: str, deployment_id: str, state: AuthorityState) -> None:
        conn = self._connect(path)
        try:
            conn.execute("BEGIN IMMEDIATE")
            conn.execute(
                "INSERT INTO recovery_watermark(deployment_id,epoch,sequence,fingerprint) VALUES (?,?,?,?) "
                "ON CONFLICT(deployment_id) DO UPDATE SET epoch=excluded.epoch, sequence=excluded.sequence, fingerprint=excluded.fingerprint",
                (deployment_id, state.epoch, state.sequence, state.fingerprint),
            )
            conn.execute("COMMIT")
        except Exception:
            try:
                conn.execute("ROLLBACK")
            except Exception:
                pass
            raise
        finally:
            conn.close()

    def accept(self, deployment_id: str, state: AuthorityState) -> str:
        # Check the strongest known state first. Anchor is written before local,
        # making interrupted updates conservative: the anchor may be ahead, but
        # the local store cannot silently restore older authority.
        current = self.read(deployment_id)
        comparison = self._compare(current, state)
        if comparison:
            return comparison
        self._write(self.anchor_path, deployment_id, state)
        self._write(self.db_path, deployment_id, state)
        return "ACCEPTED"


class RecoveryAuthorityGate:
    def __init__(self, active_profile: AuthorityTrustProfile, store: RecoveryWatermarkStore, requester_service_id: str = "REQUESTING_AI"):
        self.active_profile = active_profile
        self.store = store
        self.requester_service_id = requester_service_id

    def evaluate(self, supplied_profile: AuthorityTrustProfile, state: AuthorityState) -> RecoveryEvidence:
        accepted = None
        read_failed = False
        try:
            accepted = self.store.read(self.active_profile.deployment_id)
        except Exception:
            read_failed = True

        accepted_epoch = accepted[0] if accepted else None
        accepted_sequence = accepted[1] if accepted else None

        def safe_fingerprint() -> str | None:
            try:
                return state.fingerprint
            except Exception:
                return None

        def result(status: str, reason: str) -> RecoveryEvidence:
            return RecoveryEvidence(
                status,
                reason,
                state.service_id,
                supplied_profile.profile_id,
                supplied_profile.profile_version,
                state.epoch if type(state.epoch) is int else None,
                state.sequence if type(state.sequence) is int else None,
                accepted_epoch,
                accepted_sequence,
                safe_fingerprint(),
                supplied_profile.independence_level,
            )

        if read_failed:
            return result("INDETERMINATE", "persistent authority high-watermark unavailable")
        if supplied_profile != self.active_profile:
            return result("PREVENTED", "trust profile is not exact active profile")
        if not (0 <= supplied_profile.independence_level <= MAX_DEMONSTRATED_INDEPENDENCE_LEVEL):
            return result("PREVENTED", "declared independence level exceeds reference-harness evidence")
        if state.service_id == self.requester_service_id:
            return result("PREVENTED", "requesting service cannot become runtime authority")
        if state.service_id not in self.active_profile.authorised_service_ids:
            return result("PREVENTED", "authority service identity not authorised")
        if type(state.epoch) is not int or type(state.sequence) is not int or state.epoch < 0 or state.sequence < 0:
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
