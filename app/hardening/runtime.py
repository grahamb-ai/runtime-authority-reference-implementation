from __future__ import annotations

import threading
import uuid
from datetime import datetime, timedelta, timezone

from .models import AuthorityReceipt, ExactClinicalCommit, ProtectedClinicalBind

BIND_LIFETIME_SECONDS = 30


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
    return ProtectedClinicalBind(
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
