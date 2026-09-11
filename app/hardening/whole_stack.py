from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass
from datetime import datetime, timezone

from .deployment_enforcement import DeploymentEnforcer, EnforcementEvidence, DeploymentBoundaryProfile, BreakGlassAuthority
from .models import ExactClinicalCommit, ProtectedClinicalBind

REFERENCE_COMPOSITION_KEY = b"asvh-reference-composition-only"
COMPOSITION_EVIDENCE_MAX_AGE_SECONDS = 30


@dataclass(frozen=True)
class LayerAuthorityEvidence:
    layer: str
    producer_id: str
    deployment_id: str
    commit_binding_hash: str
    status: str
    observed_at: str
    integrity_reference: str = ""

    def payload(self) -> str:
        return json.dumps({
            "layer": self.layer,
            "producer_id": self.producer_id,
            "deployment_id": self.deployment_id,
            "commit_binding_hash": self.commit_binding_hash,
            "status": self.status,
            "observed_at": self.observed_at,
        }, sort_keys=True, separators=(",", ":"))


def make_layer_authority_evidence(*, layer: str, producer_id: str, deployment_id: str, commit_binding_hash: str, status: str, observed_at: str) -> LayerAuthorityEvidence:
    unsigned = LayerAuthorityEvidence(layer, producer_id, deployment_id, commit_binding_hash, status, observed_at)
    digest = hmac.new(REFERENCE_COMPOSITION_KEY, unsigned.payload().encode("utf-8"), hashlib.sha256).hexdigest()
    return LayerAuthorityEvidence(layer, producer_id, deployment_id, commit_binding_hash, status, observed_at, f"WS-HMAC-SHA256-1:{digest}")


def verify_layer_authority_evidence(evidence: LayerAuthorityEvidence) -> bool:
    if not evidence.integrity_reference.startswith("WS-HMAC-SHA256-1:"):
        return False
    supplied = evidence.integrity_reference.split(":", 1)[1]
    expected = hmac.new(REFERENCE_COMPOSITION_KEY, LayerAuthorityEvidence(
        evidence.layer,
        evidence.producer_id,
        evidence.deployment_id,
        evidence.commit_binding_hash,
        evidence.status,
        evidence.observed_at,
    ).payload().encode("utf-8"), hashlib.sha256).hexdigest()
    return hmac.compare_digest(supplied, expected)


@dataclass(frozen=True)
class WholeStackAuthorityContext:
    distributed_status: str | None
    policy_status: str | None
    present_standing_status: str | None
    authority_policy_version: str
    authority_rule_catalogue_version: str
    distributed_authority_epoch: int | None = None
    current_distributed_epoch: int | None = None
    recovery_authority_status: str | None = None
    evidence_contract_status: str | None = None
    distributed_deployment_id: str | None = None
    recovery_deployment_id: str | None = None
    evidence_deployment_id: str | None = None
    policy_deployment_id: str | None = None
    evidence_subject_ref: str | None = None
    evidence_product_identifier: str | None = None
    evidence_product_version: str | None = None
    authority_commit_binding_hash: str | None = None
    layer_evidence: tuple[LayerAuthorityEvidence, ...] = ()


@dataclass(frozen=True)
class WholeStackEvidence:
    status: str
    decisive_layer: str
    detail: str
    deployment_evidence: EnforcementEvidence | None = None


def _parse_ts(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


class WholeStackExecutionCoordinator:
    """Reference composition boundary for HARDEN-001 through HARDEN-009.

    Upstream authority results and their cross-layer identities are re-composed
    as decisive execution prerequisites. This is a reference-harness mechanism,
    not a production transaction, consensus, identity-provider, or NHS/EPR
    non-bypassability claim.
    """

    def __init__(self, enforcer: DeploymentEnforcer):
        self.enforcer = enforcer

    @staticmethod
    def _blocked(layer: str, detail: str, *, indeterminate: bool = False) -> WholeStackEvidence:
        return WholeStackEvidence("INDETERMINATE" if indeterminate else "PREVENTED", layer, detail, None)

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
        identity_values = (
            context.distributed_deployment_id,
            context.recovery_deployment_id,
            context.evidence_deployment_id,
            context.policy_deployment_id,
            context.evidence_subject_ref,
            context.evidence_product_identifier,
            context.evidence_product_version,
            context.authority_commit_binding_hash,
        )
        if any(value is None for value in identity_values):
            return self._blocked("IDENTITY_COHERENCE", "required cross-layer identity binding absent", indeterminate=True)

        expected_deployment = self.enforcer.active_profile.deployment_id
        deployment_bindings = {
            "distributed": context.distributed_deployment_id,
            "recovery": context.recovery_deployment_id,
            "evidence": context.evidence_deployment_id,
            "policy": context.policy_deployment_id,
        }
        mismatched = [name for name, value in deployment_bindings.items() if value != expected_deployment]
        if mismatched:
            return self._blocked("IDENTITY_COHERENCE", f"cross-layer deployment mismatch: {','.join(mismatched)}")
        if supplied_profile.deployment_id != expected_deployment:
            return self._blocked("IDENTITY_COHERENCE", "supplied deployment profile identity differs from active deployment")
        if context.evidence_subject_ref != commit.patient_ref:
            return self._blocked("IDENTITY_COHERENCE", "contracted evidence subject differs from exact consequence subject")
        if context.evidence_product_identifier != commit.product_identifier:
            return self._blocked("IDENTITY_COHERENCE", "contracted evidence product differs from exact consequence product")
        if context.evidence_product_version != commit.product_version:
            return self._blocked("IDENTITY_COHERENCE", "contracted evidence product version differs from exact consequence product version")
        if context.authority_commit_binding_hash != commit.commit_binding_hash:
            return self._blocked("IDENTITY_COHERENCE", "authority consequence binding differs from exact consequence")

        if context.distributed_status is None:
            return self._blocked("DISTRIBUTED_AUTHORITY", "distributed authority result absent", indeterminate=True)
        if context.distributed_status == "INDETERMINATE":
            return self._blocked("DISTRIBUTED_AUTHORITY", "distributed authority indeterminate", indeterminate=True)
        if context.distributed_status != "ACTIVE":
            return self._blocked("DISTRIBUTED_AUTHORITY", f"distributed authority not active: {context.distributed_status}")
        if context.distributed_authority_epoch is None or context.current_distributed_epoch is None:
            return self._blocked("DISTRIBUTED_AUTHORITY", "distributed authority epoch unavailable", indeterminate=True)
        if context.distributed_authority_epoch != context.current_distributed_epoch:
            return self._blocked("DISTRIBUTED_AUTHORITY", "execution context fenced by current distributed authority epoch")

        if context.recovery_authority_status is None:
            return self._blocked("RECOVERY_AUTHORITY", "recovery authority result absent", indeterminate=True)
        if context.recovery_authority_status == "INDETERMINATE":
            return self._blocked("RECOVERY_AUTHORITY", "recovery authority indeterminate", indeterminate=True)
        if context.recovery_authority_status != "ACTIVE":
            return self._blocked("RECOVERY_AUTHORITY", f"recovery authority not active: {context.recovery_authority_status}")

        if context.evidence_contract_status is None:
            return self._blocked("EVIDENCE_CONTRACT", "contracted evidence result absent", indeterminate=True)
        if context.evidence_contract_status == "INDETERMINATE":
            return self._blocked("EVIDENCE_CONTRACT", "contracted evidence indeterminate", indeterminate=True)
        if context.evidence_contract_status == "ESCALATE":
            return self._blocked("EVIDENCE_CONTRACT", "contracted evidence requires escalation")
        if context.evidence_contract_status != "ALLOW":
            return self._blocked("EVIDENCE_CONTRACT", f"contracted evidence not admissible: {context.evidence_contract_status}")

        if context.policy_status is None:
            return self._blocked("POLICY_TRANSITION", "policy-transition result absent", indeterminate=True)
        if context.policy_status == "INDETERMINATE":
            return self._blocked("POLICY_TRANSITION", "policy transition indeterminate", indeterminate=True)
        if context.policy_status == "REVALIDATE":
            return self._blocked("POLICY_TRANSITION", "fresh authority required after policy transition")
        if context.policy_status != "ALLOW":
            return self._blocked("POLICY_TRANSITION", f"policy transition prevents outstanding authority: {context.policy_status}")

        if context.present_standing_status is None:
            return self._blocked("PRESENT_STANDING", "present-standing result absent", indeterminate=True)
        if context.present_standing_status == "INDETERMINATE":
            return self._blocked("PRESENT_STANDING", "present standing indeterminate", indeterminate=True)
        if context.present_standing_status != "ALLOW":
            return self._blocked("PRESENT_STANDING", f"present standing not admissible: {context.present_standing_status}")

        if original_decision == "ALLOW":
            if bind is None:
                return self._blocked("PROTECTED_BIND", "ALLOW path missing protected bind")
            try:
                issued_at = _parse_ts(bind.issued_at)
                expires_at = _parse_ts(bind.expires_at)
                effective_now = now if now.tzinfo is not None else now.replace(tzinfo=timezone.utc)
                effective_now = effective_now.astimezone(timezone.utc)
            except Exception:
                return self._blocked("PROTECTED_BIND", "protected bind temporal state malformed", indeterminate=True)
            if effective_now < issued_at:
                return self._blocked("PROTECTED_BIND", "protected bind not yet valid")
            if effective_now >= expires_at:
                return self._blocked("PROTECTED_BIND", "protected bind expired")
            if expires_at <= issued_at:
                return self._blocked("PROTECTED_BIND", "protected bind temporal interval invalid")
            if bind.commit_id != commit.commit_id or bind.commit_binding_hash != commit.commit_binding_hash:
                return self._blocked("PROTECTED_BIND", "protected bind does not match exact commit")
            if bind.runtime_policy_version != context.authority_policy_version:
                return self._blocked("POLICY_BINDING", "protected bind policy basis differs from authority context")
            if bind.rule_catalogue_version != context.authority_rule_catalogue_version:
                return self._blocked("POLICY_BINDING", "protected bind rule catalogue differs from authority context")
            if commit.runtime_policy_version != context.authority_policy_version:
                return self._blocked("POLICY_BINDING", "exact commit policy basis differs from authority context")
            if commit.rule_catalogue_version != context.authority_rule_catalogue_version:
                return self._blocked("POLICY_BINDING", "exact commit rule catalogue differs from authority context")

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
