from __future__ import annotations

import hashlib
import threading
from dataclasses import dataclass
from typing import Any

from .models import AuthorityReceipt, ExactClinicalCommit, ProtectedClinicalBind
from .runtime import verify_bind_integrity


def consequence_key(commit: ExactClinicalCommit) -> str:
    material = f"{commit.commit_id}|{commit.commit_binding_hash}|{commit.target_system}|{commit.target_instance}|{commit.target_record_ref}"
    return "ck:" + hashlib.sha256(material.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ClinicalConsequenceEvidence:
    consequence_key: str
    consequence_status: str  # FORMED | PREVENTED | INDETERMINATE
    bind_id: str
    authority_receipt_id: str
    commit_id: str
    commit_binding_hash: str
    target_record_ref: str
    provenance_level: str
    target_reference: str | None = None
    detail: str = ""


class ReconcilableEPRSimulator:
    """Reference target with idempotent consequence formation and authoritative read-back."""

    def __init__(self):
        self._lock = threading.Lock()
        self._records: dict[str, dict[str, Any]] = {}
        self._attempts: dict[str, int] = {}

    def commit(self, key: str, commit: ExactClinicalCommit, *, lose_ack: bool = False, fail_before_write: bool = False) -> dict[str, Any]:
        with self._lock:
            self._attempts[key] = self._attempts.get(key, 0) + 1
            if fail_before_write:
                raise TimeoutError("simulated transport failure before target write")
            if key not in self._records:
                self._records[key] = {
                    "target_reference": f"SIM-{len(self._records)+1}",
                    "commit_id": commit.commit_id,
                    "commit_binding_hash": commit.commit_binding_hash,
                    "target_record_ref": commit.target_record_ref,
                }
            record = dict(self._records[key])
        if lose_ack:
            raise TimeoutError("simulated acknowledgement loss after target write")
        return record

    def read_by_key(self, key: str) -> dict[str, Any] | None:
        with self._lock:
            record = self._records.get(key)
            return dict(record) if record is not None else None

    def delete_for_test(self, key: str) -> None:
        with self._lock:
            self._records.pop(key, None)

    def record_count(self) -> int:
        with self._lock:
            return len(self._records)

    def attempt_count(self, key: str) -> int:
        with self._lock:
            return self._attempts.get(key, 0)


def authority_chain_valid(bind: ProtectedClinicalBind, receipt: AuthorityReceipt, commit: ExactClinicalCommit) -> bool:
    return (
        verify_bind_integrity(bind)
        and receipt.decision == "ALLOW"
        and bind.authority_receipt_id == receipt.receipt_id
        and bind.commit_id == commit.commit_id
        and bind.commit_binding_hash == commit.commit_binding_hash
        and receipt.commit_id == commit.commit_id
        and receipt.commit_binding_hash == commit.commit_binding_hash
        and bind.runtime_policy_version == commit.runtime_policy_version
        and receipt.runtime_policy_version == commit.runtime_policy_version
        and bind.rule_catalogue_version == commit.rule_catalogue_version
        and receipt.rule_catalogue_version == commit.rule_catalogue_version
    )


class ConsequenceReconciler:
    def __init__(self, target: ReconcilableEPRSimulator):
        self.target = target

    def _evidence(self, status: str, bind: ProtectedClinicalBind, receipt: AuthorityReceipt, commit: ExactClinicalCommit, key: str, *, target_reference: str | None = None, detail: str = "", provenance_level: str | None = None) -> ClinicalConsequenceEvidence:
        if provenance_level is None:
            provenance_level = "CE-3-TARGET-READBACK" if target_reference else "CE-2-TARGET-ABSENCE"
        return ClinicalConsequenceEvidence(
            consequence_key=key,
            consequence_status=status,
            bind_id=bind.bind_id,
            authority_receipt_id=receipt.receipt_id,
            commit_id=commit.commit_id,
            commit_binding_hash=commit.commit_binding_hash,
            target_record_ref=commit.target_record_ref,
            provenance_level=provenance_level,
            target_reference=target_reference,
            detail=detail,
        )

    def reconcile(self, bind: ProtectedClinicalBind, receipt: AuthorityReceipt, commit: ExactClinicalCommit) -> ClinicalConsequenceEvidence:
        key = consequence_key(commit)
        if not authority_chain_valid(bind, receipt, commit):
            return self._evidence("PREVENTED", bind, receipt, commit, key, detail="AUTHORITY_CHAIN_INVALID", provenance_level="CE-0-CHAIN-VALIDATION")
        try:
            record = self.target.read_by_key(key)
        except TimeoutError as exc:
            return self._evidence("INDETERMINATE", bind, receipt, commit, key, detail=f"target read-back unavailable: {exc}", provenance_level="CE-1-RECONCILIATION-UNAVAILABLE")
        if record is None:
            return self._evidence("PREVENTED", bind, receipt, commit, key, detail="authoritative simulator read-back found no consequence")
        if (
            record.get("commit_binding_hash") != commit.commit_binding_hash
            or record.get("commit_id") != commit.commit_id
            or record.get("target_record_ref") != commit.target_record_ref
        ):
            return self._evidence("INDETERMINATE", bind, receipt, commit, key, target_reference=record.get("target_reference"), detail="target evidence conflicts with exact commit")
        return self._evidence("FORMED", bind, receipt, commit, key, target_reference=record.get("target_reference"), detail="authoritative simulator read-back confirmed exact consequence")


class ConsequenceAwareExecutor:
    def __init__(self, target: ReconcilableEPRSimulator, reconciler: ConsequenceReconciler):
        self.target = target
        self.reconciler = reconciler

    def execute(self, bind: ProtectedClinicalBind, receipt: AuthorityReceipt, commit: ExactClinicalCommit, *, lose_ack: bool = False, fail_before_write: bool = False, auto_reconcile: bool = True) -> ClinicalConsequenceEvidence:
        key = consequence_key(commit)
        if not authority_chain_valid(bind, receipt, commit):
            return ClinicalConsequenceEvidence(
                consequence_key=key,
                consequence_status="PREVENTED",
                bind_id=bind.bind_id,
                authority_receipt_id=receipt.receipt_id,
                commit_id=commit.commit_id,
                commit_binding_hash=commit.commit_binding_hash,
                target_record_ref=commit.target_record_ref,
                provenance_level="CE-0-CHAIN-VALIDATION",
                detail="AUTHORITY_CHAIN_INVALID",
            )
        try:
            record = self.target.commit(key, commit, lose_ack=lose_ack, fail_before_write=fail_before_write)
            return ClinicalConsequenceEvidence(
                consequence_key=key,
                consequence_status="FORMED",
                bind_id=bind.bind_id,
                authority_receipt_id=receipt.receipt_id,
                commit_id=commit.commit_id,
                commit_binding_hash=commit.commit_binding_hash,
                target_record_ref=commit.target_record_ref,
                provenance_level="CE-2-TARGET-ACK",
                target_reference=record.get("target_reference"),
                detail="target acknowledgement received",
            )
        except TimeoutError as exc:
            if auto_reconcile:
                return self.reconciler.reconcile(bind, receipt, commit)
            return ClinicalConsequenceEvidence(
                consequence_key=key,
                consequence_status="INDETERMINATE",
                bind_id=bind.bind_id,
                authority_receipt_id=receipt.receipt_id,
                commit_id=commit.commit_id,
                commit_binding_hash=commit.commit_binding_hash,
                target_record_ref=commit.target_record_ref,
                provenance_level="CE-1-EXECUTOR-OBSERVATION",
                detail=str(exc),
            )
