from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .deployment_enforcement import DeploymentEnforcer, EnforcementEvidence, DeploymentBoundaryProfile, BreakGlassAuthority
from .models import ExactClinicalCommit, ProtectedClinicalBind


@dataclass(frozen=True)
class WholeStackAuthorityContext:
    distributed_status: str | None
    policy_status: str | None
    present_standing_status: str | None
    authority_policy_version: str
    authority_rule_catalogue_version: str
    distributed_authority_epoch: int | None = None
    current_distributed_epoch: int | None = None


@dataclass(frozen=True)
class WholeStackEvidence:
    status: str
    decisive_layer: str
    detail: str
    deployment_evidence: EnforcementEvidence | None = None


class WholeStackExecutionCoordinator:
    """Initial whole-stack composition point.

    Baseline intentionally contains only the existing deployment enforcement
    delegation. Frozen hostile tests determine whether cross-layer state is
    sufficiently bound before consequence formation.
    """

    def __init__(self, enforcer: DeploymentEnforcer):
        self.enforcer = enforcer

    def execute(
        self,
        *,
        context: WholeStackAuthorityContext,
        supplied_profile: DeploymentBoundaryProfile,
        route_id: str,
        target_capability: str,
        commit: ExactClinicalCommit,
        bind: ProtectedClinicalBind | None,
        original_decision: str,
        control_contract_version: str,
        now: datetime,
        break_glass: BreakGlassAuthority | None = None,
    ) -> WholeStackEvidence:
        deployment = self.enforcer.enforce(
            supplied_profile=supplied_profile,
            route_id=route_id,
            target_capability=target_capability,
            commit=commit,
            bind=bind,
            original_decision=original_decision,
            control_contract_version=control_contract_version,
            now=now,
            break_glass=break_glass,
        )
        return WholeStackEvidence(deployment.status, "DEPLOYMENT", deployment.detail, deployment)
