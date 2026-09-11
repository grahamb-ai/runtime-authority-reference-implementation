from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import FrozenSet

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
    def __init__(self, active_profile: DeploymentBoundaryProfile):
        self.active_profile = active_profile

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
        if not supplied_profile.integrity_valid:
            return evidence("PREVENTED", "deployment profile integrity invalid")
        if supplied_profile.deployment_id != self.active_profile.deployment_id:
            return evidence("PREVENTED", "deployment profile deployment mismatch")
        if supplied_profile.profile_version != self.active_profile.profile_version:
            return evidence("PREVENTED", "deployment profile version not active")
        if control_contract_version != supplied_profile.active_control_contract_version:
            return evidence("PREVENTED", "control contract version not authorised by profile")

        route = supplied_profile.binding_for(route_id)
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
        if break_glass.deployment_id != supplied_profile.deployment_id:
            return evidence("PREVENTED", "break-glass deployment mismatch")
        if break_glass.policy_version != supplied_profile.break_glass_policy_version:
            return evidence("PREVENTED", "break-glass policy version mismatch")
        if break_glass.commit_binding_hash != commit.commit_binding_hash:
            return evidence("PREVENTED", "break-glass exact consequence mismatch")
        if now > datetime.fromisoformat(break_glass.expires_at):
            return evidence("PREVENTED", "break-glass expired")
        return evidence("FORMED", "separate break-glass authority accepted", break_glass.override_id)
