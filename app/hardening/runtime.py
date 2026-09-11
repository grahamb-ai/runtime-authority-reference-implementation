from __future__ import annotations

import hashlib
import hmac
import threading
import uuid
from dataclasses import asdict, replace
from datetime import datetime, timedelta, timezone

from .models import AuthorityReceipt, ExactClinicalCommit, ProtectedClinicalBind, canonical_json

BIND_LIFETIME_SECONDS = 30

# Reference-harness key only. This is deliberately not a production key-management design.
REFERENCE_BIND_INTEGRITY_KEY = b"asvh-harden-001-reference-key-not-for-production"
BIND_INTEGRITY_PROFILE = "PCB-HMAC-SHA256-1"


class HarnessClock:
    def __init__(self, initial: datetime | None = None):
        self._lock = threading.Lock()
        self._now = initial or datetime.now(timezone.utc)

    def now(self) -> datetime:
        with self._lock:
            return self._now

    def advance(self, seconds: int) -> None:
        with self._lock:
            self._now += timedelta(seconds=seconds)


def _bind_integrity_payload(bind: ProtectedClinicalBind) -> str:
    data = asdict(bind)
    data.pop("integrity_reference", None)
    return canonical_json(data)


def compute_bind_integrity(
    bind: ProtectedClinicalBind,
    key: bytes = REFERENCE_BIND_INTEGRITY_KEY,
) -> str:
    digest = hmac.new(
        key,
        _bind_integrity_payload(bind).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"{BIND_INTEGRITY_PROFILE}:{digest}"


def verify_bind_integrity(
    bind: ProtectedClinicalBind,
    key: bytes = REFERENCE_BIND_INTEGRITY_KEY,
) -> bool:
    if not isinstance(bind.integrity_reference, str) or not bind.integrity_reference:
        return False
    expected = compute_bind_integrity(bind, key)
    return hmac.compare_digest(bind.integrity_reference, expected)


def make_authority_receipt(
    decision: str,
    commit: ExactClinicalCommit,
    clock: HarnessClock,
    runtime_authority_version: str = "ASVH-RA-1.0",
) -> AuthorityReceipt:
    return AuthorityReceipt(
        receipt_id=str(uuid.uuid4()),
        decision=decision,
        commit_id=commit.commit_id,
        commit_binding_hash=commit.commit_binding_hash,
        materiality_profile=commit.materiality_profile,
        canonicalisation_profile=commit.canonicalisation_profile,
        runtime_authority_version=runtime_authority_version,
        runtime_policy_version=commit.runtime_policy_version,
        rule_catalogue_version=commit.rule_catalogue_version,
        issued_at=clock.now().isoformat(),
    )


def make_protected_bind(
    receipt: AuthorityReceipt,
    commit: ExactClinicalCommit,
    clock: HarnessClock,
    lifetime_seconds: int = BIND_LIFETIME_SECONDS,
) -> ProtectedClinicalBind | None:
    if receipt.decision != "ALLOW":
        return None
    if receipt.commit_binding_hash != commit.commit_binding_hash:
        return None
    issued = clock.now()
    unsigned = ProtectedClinicalBind(
        schema_version="PCB-1.0",
        bind_id=str(uuid.uuid4()),
        authority_receipt_id=receipt.receipt_id,
        commit_id=commit.commit_id,
        commit_binding_hash=commit.commit_binding_hash,
        runtime_authority_version=receipt.runtime_authority_version,
        runtime_policy_version=commit.runtime_policy_version,
        rule_catalogue_version=commit.rule_catalogue_version,
        materiality_profile=commit.materiality_profile,
        canonicalisation_profile=commit.canonicalisation_profile,
        issued_at=issued.isoformat(),
        expires_at=(issued + timedelta(seconds=lifetime_seconds)).isoformat(),
    )
    return replace(unsigned, integrity_reference=compute_bind_integrity(unsigned))
