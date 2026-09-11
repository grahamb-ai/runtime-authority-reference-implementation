from __future__ import annotations

import threading
import uuid
from datetime import datetime
from typing import Any

from .models import ExactClinicalCommit
from .runtime import HarnessClock, verify_bind_integrity
from .store import BindStore


class EPRSimulator:
    def __init__(self):
        self._lock = threading.Lock()
        self._consequences: list[dict[str, Any]] = []

    def commit(self, exact_commit: ExactClinicalCommit) -> dict[str, Any]:
        consequence = {
            "consequence_id": str(uuid.uuid4()),
            "commit_id": exact_commit.commit_id,
            "patient_ref": exact_commit.patient_ref,
            "encounter_ref": exact_commit.encounter_ref,
            "clinician_ref": exact_commit.clinician_ref,
            "document_hash": exact_commit.document_hash,
            "target_record_ref": exact_commit.target_record_ref,
        }
        with self._lock:
            self._consequences.append(consequence)
        return consequence

    @property
    def commit_count(self) -> int:
        with self._lock:
            return len(self._consequences)

    def all_consequences(self) -> list[dict[str, Any]]:
        with self._lock:
            return list(self._consequences)


class ProtectedExecutor:
    def __init__(self, store: BindStore, simulator: EPRSimulator, clock: HarnessClock):
        self.store = store
        self.simulator = simulator
        self.clock = clock

    def execute(self, bind_id: str, attempted_commit: ExactClinicalCommit) -> str:
        current = self.store.get(bind_id)
        if current is None:
            return "NO_VALID_BIND"
        bind, status = current

        # Integrity is checked before a persisted record is treated as execution authority.
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

        if not self.store.claim(bind.bind_id, now.isoformat()):
            return "ATOMIC_CLAIM_FAILED"

        try:
            self.simulator.commit(attempted_commit)
            self.store.set_status(bind.bind_id, "CONSUMED", self.clock.now().isoformat())
            return "EXECUTED"
        except Exception:
            self.store.set_status(bind.bind_id, "INDETERMINATE", self.clock.now().isoformat())
            return "EXECUTION_INDETERMINATE"
