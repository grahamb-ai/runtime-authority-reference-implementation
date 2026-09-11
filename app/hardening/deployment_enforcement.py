from __future__ import annotations

import threading
from dataclasses import dataclass
from datetime import datetime

from .models import ExactClinicalCommit, ProtectedClinicalBind


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
    substitution. Break-glass single-use is enforced atomically within this
    enforcer instance. This is a bounded harness mechanism, not production IAM
    or distributed replay protection.
    """

    def __init__(self, active_profile: DeploymentBoundaryProfile):
        self.active_profile = active_profile
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

        # Exact active-profile binding prevents same-version substitution of
        # route sets, profile identity, contract version or break-glass policy.
        if supplied_profile != self.active_profile:
            return evidence("PREVENTED", "supplied deployment profile is not the active authoritative profile")

        if control_contract_version != self.active_profile.active_control_contract_version:
            return evidence("PREVENTED", "control contract version not authorised by active profile")

        route = self.active_profile.binding_for(route_id)
        if route is None:
            return evidence("PREVENTED", "route not declared in deployment boundary")
        if route.target_capability != target_capability:
            return evidence("PREVENTED", "route target capability mismatch")

        if original_decision == "ALLOW":
            if bind is None:
                return evidence("PREVENTED", "ALLOW without protected bind")
            if bind.commit_binding_hash != commit.commit_binding_hash:
                return evidence("PREVENTED", "protected bind does not match exact commit")
            return evidence("FORMED", "protected route authorised exact consequence")

        if break_glass is None:
            return evidence("PREVENTED", "non-ALLOW decision has no separate break-glass authority")
        if break_glass.deployment_id != self.active_profile.deployment_id:
            return evidence("PREVENTED", "break-glass deployment mismatch")
        if break_glass.policy_version != self.active_profile.break_glass_policy_version:
            return evidence("PREVENTED", "break-glass policy version mismatch")
        if break_glass.commit_binding_hash != commit.commit_binding_hash:
            return evidence("PREVENTED", "break-glass exact consequence mismatch")
        if not break_glass.authority_identity:
            return evidence("PREVENTED", "break-glass authority identity missing")

        try:
            issued_at = datetime.fromisoformat(break_glass.issued_at)
            expires_at = datetime.fromisoformat(break_glass.expires_at)
        except (TypeError, ValueError):
            return evidence("PREVENTED", "break-glass temporal evidence invalid")
        if now < issued_at:
            return evidence("PREVENTED", "break-glass not yet valid")
        if now > expires_at:
            return evidence("PREVENTED", "break-glass expired")
        if expires_at < issued_at:
            return evidence("PREVENTED", "break-glass temporal interval invalid")

        with self._lock:
            if break_glass.single_use:
                if break_glass.override_id in self._consumed_break_glass:
                    return evidence("PREVENTED", "break-glass replay rejected", break_glass.override_id)
                self._consumed_break_glass.add(break_glass.override_id)

        return evidence("FORMED", "separate break-glass authority accepted", break_glass.override_id)
