from __future__ import annotations

import hashlib
import hmac
import json
import threading
from dataclasses import dataclass, replace
from datetime import datetime

from .models import ExactClinicalCommit, ProtectedClinicalBind
from .store import BreakGlassUseStore

REFERENCE_BREAK_GLASS_KEY = b"asvh-reference-break-glass-only"
BREAK_GLASS_INTEGRITY_PROFILE = "BG-HMAC-SHA256-1"
VALID_RUNTIME_DECISIONS = ("ALLOW", "ESCALATE", "REFUSE")


@dataclass(frozen=True)
class RouteBinding:
    route_id: str
    target_capability: str


@dataclass(frozen=True)
class DeploymentBoundaryProfile:
    profile_id: str
    profile_version: int
    deployment_id: str
    governed_consequence_type: str
    active_control_contract_version: str
    protected_routes: tuple[RouteBinding, ...]
    break_glass_policy_version: str
    break_glass_max_validity_seconds: int = 900
    break_glass_authority_identities: tuple[str, ...] = (
        "CLINICAL-DUTY-MANAGER",
        "DUTY-CONSULTANT",
    )
    integrity_valid: bool = True

    def binding_for(self, route_id: str) -> RouteBinding | None:
        return next((r for r in self.protected_routes if r.route_id == route_id), None)


@dataclass(frozen=True)
class BreakGlassAuthority:
    override_id: str
    authority_identity: str
    commit_binding_hash: str
    deployment_id: str
    issued_at: str
    expires_at: str
    policy_version: str
    single_use: bool = True
    integrity_reference: str = ""


def _break_glass_payload(authority: BreakGlassAuthority) -> str:
    return json.dumps(
        {
            "override_id": authority.override_id,
            "authority_identity": authority.authority_identity,
            "commit_binding_hash": authority.commit_binding_hash,
            "deployment_id": authority.deployment_id,
            "issued_at": authority.issued_at,
            "expires_at": authority.expires_at,
            "policy_version": authority.policy_version,
            "single_use": authority.single_use,
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def compute_break_glass_integrity(
    authority: BreakGlassAuthority,
    key: bytes = REFERENCE_BREAK_GLASS_KEY,
) -> str:
    digest = hmac.new(
        key,
        _break_glass_payload(authority).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"{BREAK_GLASS_INTEGRITY_PROFILE}:{digest}"


def sign_break_glass_authority(
    authority: BreakGlassAuthority,
    key: bytes = REFERENCE_BREAK_GLASS_KEY,
) -> BreakGlassAuthority:
    unsigned = replace(authority, integrity_reference="")
    return replace(unsigned, integrity_reference=compute_break_glass_integrity(unsigned, key))


def verify_break_glass_integrity(
    authority: BreakGlassAuthority,
    key: bytes = REFERENCE_BREAK_GLASS_KEY,
) -> bool:
    if not authority.integrity_reference.startswith(f"{BREAK_GLASS_INTEGRITY_PROFILE}:"):
        return False
    supplied = authority.integrity_reference.split(":", 1)[1]
    unsigned = replace(authority, integrity_reference="")
    expected = compute_break_glass_integrity(unsigned, key).split(":", 1)[1]
    return hmac.compare_digest(supplied, expected)


@dataclass(frozen=True)
class EnforcementEvidence:
    status: str  # FORMED | PREVENTED | INDETERMINATE
    route_id: str
    target_capability: str
    deployment_profile_id: str
    deployment_profile_version: int
    control_contract_version: str
    original_decision: str
    break_glass_override_id: str | None
    detail: str


class DeploymentEnforcer:
    """Reference-harness deployment boundary enforcer.

    The active profile is constructor-bound. A caller-supplied profile must be
    exactly the active immutable profile; matching only version/deployment is
    insufficient because it would permit same-version route or contract
    substitution. Runtime decision vocabulary is closed and exact. Break-glass
    authority must be integrity-bound, carry an authority identity explicitly
    admitted by the active profile and a non-blank override identifier, use
    timezone-aware temporal evidence, remain inside the profile-bound maximum
    validity interval, and carry explicit SINGLE_USE semantics. The validity
    interval is half-open: issued_at is inclusive and expires_at is exclusive.
    Consumption is enforced atomically inside this enforcer by default and can
    be extended across enforcer instances and restart by supplying a shared
    BreakGlassUseStore.

    This is a bounded harness mechanism, not production IAM, key management,
    external monotonic storage or distributed consensus.
    """

    def __init__(
        self,
        active_profile: DeploymentBoundaryProfile,
        break_glass_store: BreakGlassUseStore | None = None,
    ):
        self.active_profile = active_profile
        self.break_glass_store = break_glass_store
        self._lock = threading.Lock()
        self._consumed_break_glass: set[str] = set()

    def enforce(
        self,
        *,
        supplied_profile: DeploymentBoundaryProfile,
        route_id: str,
        target_capability: str,
        commit: ExactClinicalCommit,
        bind: ProtectedClinicalBind | None,
        original_decision: str,
        control_contract_version: str,
        now: datetime,
        break_glass: BreakGlassAuthority | None = None,
        enforcement_available: bool = True,
    ) -> EnforcementEvidence:
        def evidence(status: str, detail: str, override: str | None = None) -> EnforcementEvidence:
            return EnforcementEvidence(
                status=status,
                route_id=route_id,
                target_capability=target_capability,
                deployment_profile_id=supplied_profile.profile_id,
                deployment_profile_version=supplied_profile.profile_version,
                control_contract_version=control_contract_version,
                original_decision=original_decision,
                break_glass_override_id=override,
                detail=detail,
            )

        if not enforcement_available:
            return evidence("PREVENTED", "deployment enforcement unavailable; fail closed")
        if not self.active_profile.integrity_valid or not supplied_profile.integrity_valid:
            return evidence("PREVENTED", "deployment profile integrity invalid")
        if supplied_profile != self.active_profile:
            return evidence("PREVENTED", "supplied deployment profile is not the active authoritative profile")
        if control_contract_version != self.active_profile.active_control_contract_version:
            return evidence("PREVENTED", "control contract version not authorised by active profile")

        route = self.active_profile.binding_for(route_id)
        if route is None:
            return evidence("PREVENTED", "route not declared in deployment boundary")
        if route.target_capability != target_capability:
            return evidence("PREVENTED", "route target capability mismatch")
        if original_decision not in VALID_RUNTIME_DECISIONS:
            return evidence("PREVENTED", "runtime decision outside closed decision vocabulary")

        if original_decision == "ALLOW":
            if bind is None:
                return evidence("PREVENTED", "ALLOW without protected bind")
            if bind.commit_binding_hash != commit.commit_binding_hash:
                return evidence("PREVENTED", "protected bind does not match exact commit")
            return evidence("FORMED", "protected route authorised exact consequence")

        if break_glass is None:
            return evidence("PREVENTED", "non-ALLOW decision has no separate break-glass authority")
        if not verify_break_glass_integrity(break_glass):
            return evidence("PREVENTED", "break-glass integrity invalid", break_glass.override_id)
        if not isinstance(break_glass.override_id, str) or not break_glass.override_id.strip():
            return evidence("PREVENTED", "break-glass override identifier missing", break_glass.override_id)
        if not isinstance(break_glass.authority_identity, str) or not break_glass.authority_identity.strip():
            return evidence("PREVENTED", "break-glass authority identity missing", break_glass.override_id)
        admitted_identities = self.active_profile.break_glass_authority_identities
        if (
            not isinstance(admitted_identities, tuple)
            or not admitted_identities
            or any(not isinstance(identity, str) or not identity.strip() for identity in admitted_identities)
            or len(set(admitted_identities)) != len(admitted_identities)
        ):
            return evidence("PREVENTED", "break-glass authority identity policy invalid", break_glass.override_id)
        if break_glass.authority_identity not in admitted_identities:
            return evidence("PREVENTED", "break-glass authority identity not admitted by active profile", break_glass.override_id)
        if break_glass.deployment_id != self.active_profile.deployment_id:
            return evidence("PREVENTED", "break-glass deployment mismatch")
        if break_glass.policy_version != self.active_profile.break_glass_policy_version:
            return evidence("PREVENTED", "break-glass policy version mismatch")
        if break_glass.commit_binding_hash != commit.commit_binding_hash:
            return evidence("PREVENTED", "break-glass exact consequence mismatch")
        if break_glass.single_use is not True:
            return evidence(
                "PREVENTED",
                "break-glass authority must be explicitly single-use",
                break_glass.override_id,
            )

        try:
            issued_at = datetime.fromisoformat(break_glass.issued_at)
            expires_at = datetime.fromisoformat(break_glass.expires_at)
        except (TypeError, ValueError):
            return evidence("PREVENTED", "break-glass temporal evidence invalid")
        if now.tzinfo is None or now.utcoffset() is None:
            return evidence("PREVENTED", "execution time must be timezone-aware", break_glass.override_id)
        if issued_at.tzinfo is None or issued_at.utcoffset() is None:
            return evidence("PREVENTED", "break-glass issued_at must be timezone-aware", break_glass.override_id)
        if expires_at.tzinfo is None or expires_at.utcoffset() is None:
            return evidence("PREVENTED", "break-glass expires_at must be timezone-aware", break_glass.override_id)
        if now < issued_at:
            return evidence("PREVENTED", "break-glass not yet valid")
        if now >= expires_at:
            return evidence("PREVENTED", "break-glass expired")
        if expires_at < issued_at:
            return evidence("PREVENTED", "break-glass temporal interval invalid")
        max_validity = self.active_profile.break_glass_max_validity_seconds
        if type(max_validity) is not int or max_validity <= 0:
            return evidence("PREVENTED", "break-glass maximum validity policy invalid", break_glass.override_id)
        if (expires_at - issued_at).total_seconds() > max_validity:
            return evidence(
                "PREVENTED",
                "break-glass validity interval exceeds active profile maximum",
                break_glass.override_id,
            )

        if self.break_glass_store is not None:
            try:
                consumed = self.break_glass_store.consume(break_glass.override_id, now.isoformat())
            except Exception:
                return evidence(
                    "PREVENTED",
                    "break-glass replay state unavailable; fail closed",
                    break_glass.override_id,
                )
            if not consumed:
                return evidence(
                    "PREVENTED",
                    "break-glass replay rejected by durable replay store",
                    break_glass.override_id,
                )
        else:
            with self._lock:
                if break_glass.override_id in self._consumed_break_glass:
                    return evidence("PREVENTED", "break-glass replay rejected", break_glass.override_id)
                self._consumed_break_glass.add(break_glass.override_id)

        return evidence("FORMED", "separate break-glass authority accepted", break_glass.override_id)
