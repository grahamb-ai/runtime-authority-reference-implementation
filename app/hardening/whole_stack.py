from __future__ import annotations

import hashlib
import hmac
import json
import threading
from dataclasses import dataclass
from datetime import datetime, timezone

from .deployment_enforcement import DeploymentEnforcer, EnforcementEvidence, DeploymentBoundaryProfile, BreakGlassAuthority
from .models import ExactClinicalCommit, ProtectedClinicalBind
from .runtime import verify_bind_integrity
from .store import BindStore

REFERENCE_COMPOSITION_KEY = b"asvh-reference-composition-only"
COMPOSITION_EVIDENCE_MAX_AGE_SECONDS = 30
EXPECTED_LAYER_PRODUCERS = {
    "DISTRIBUTED_AUTHORITY": "RA-DISTRIBUTED-01",
    "RECOVERY_AUTHORITY": "RA-RECOVERY-01",
    "EVIDENCE_CONTRACT": "RA-EVIDENCE-01",
    "POLICY_TRANSITION": "RA-POLICY-01",
    "PRESENT_STANDING": "RA-STANDING-01",
}


@dataclass(frozen=True)
class LayerAuthorityEvidence:
    layer: str
    producer_id: str
    deployment_id: str
    commit_binding_hash: str
    status: str
    observed_at: str
    authority_epoch: int | None = None
    authority_lease_id: str | None = None
    runtime_policy_version: str | None = None
    rule_catalogue_version: str | None = None
    control_contract_version: str | None = None
    deployment_profile_version: int | None = None
    integrity_reference: str = ""

    def payload(self) -> str:
        return json.dumps({
            "layer": self.layer,
            "producer_id": self.producer_id,
            "deployment_id": self.deployment_id,
            "commit_binding_hash": self.commit_binding_hash,
            "status": self.status,
            "observed_at": self.observed_at,
            "authority_epoch": self.authority_epoch,
            "authority_lease_id": self.authority_lease_id,
            "runtime_policy_version": self.runtime_policy_version,
            "rule_catalogue_version": self.rule_catalogue_version,
            "control_contract_version": self.control_contract_version,
            "deployment_profile_version": self.deployment_profile_version,
        }, sort_keys=True, separators=(",", ":"))


def make_layer_authority_evidence(
    *,
    layer: str,
    producer_id: str,
    deployment_id: str,
    commit_binding_hash: str,
    status: str,
    observed_at: str,
    authority_epoch: int | None = None,
    authority_lease_id: str | None = None,
    runtime_policy_version: str | None = None,
    rule_catalogue_version: str | None = None,
    control_contract_version: str | None = None,
    deployment_profile_version: int | None = None,
) -> LayerAuthorityEvidence:
    unsigned = LayerAuthorityEvidence(
        layer, producer_id, deployment_id, commit_binding_hash, status, observed_at,
        authority_epoch, authority_lease_id, runtime_policy_version,
        rule_catalogue_version, control_contract_version, deployment_profile_version,
    )
    digest = hmac.new(REFERENCE_COMPOSITION_KEY, unsigned.payload().encode("utf-8"), hashlib.sha256).hexdigest()
    return LayerAuthorityEvidence(
        layer, producer_id, deployment_id, commit_binding_hash, status, observed_at,
        authority_epoch, authority_lease_id, runtime_policy_version,
        rule_catalogue_version, control_contract_version, deployment_profile_version,
        f"WS-HMAC-SHA256-1:{digest}",
    )


def verify_layer_authority_evidence(evidence: LayerAuthorityEvidence) -> bool:
    if (
        not isinstance(evidence.integrity_reference, str)
        or not evidence.integrity_reference.startswith("WS-HMAC-SHA256-1:")
    ):
        return False
    supplied = evidence.integrity_reference.split(":", 1)[1]
    unsigned = LayerAuthorityEvidence(
        evidence.layer, evidence.producer_id, evidence.deployment_id,
        evidence.commit_binding_hash, evidence.status, evidence.observed_at,
        evidence.authority_epoch, evidence.authority_lease_id,
        evidence.runtime_policy_version, evidence.rule_catalogue_version,
        evidence.control_contract_version, evidence.deployment_profile_version,
    )
    expected = hmac.new(REFERENCE_COMPOSITION_KEY, unsigned.payload().encode("utf-8"), hashlib.sha256).hexdigest()
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
    distributed_lease_id: str | None = "LEASE-01"
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
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError("timestamp must be timezone-aware")
    return dt.astimezone(timezone.utc)


def _nonblank(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


class WholeStackExecutionCoordinator:
    """Reference composition boundary for HARDEN-001 through HARDEN-009.

    A shared BindStore may be supplied to extend SINGLE_USE claims across
    coordinator instances and coordinator restart. Without one, replay state is
    intentionally limited to this coordinator instance and claims must be
    bounded accordingly.
    """

    def __init__(self, enforcer: DeploymentEnforcer, bind_store: BindStore | None = None):
        self.enforcer = enforcer
        self.bind_store = bind_store
        self._bind_lock = threading.Lock()
        self._claimed_bind_ids: set[str] = set()

    @staticmethod
    def _blocked(layer: str, detail: str, *, indeterminate: bool = False) -> WholeStackEvidence:
        return WholeStackEvidence("INDETERMINATE" if indeterminate else "PREVENTED", layer, detail, None)

    def _claim_bind(self, bind: ProtectedClinicalBind, now: datetime) -> WholeStackEvidence | None:
        if self.bind_store is not None:
            try:
                stored = self.bind_store.get(bind.bind_id)
            except Exception:
                return self._blocked("PROTECTED_BIND", "durable bind claim state unavailable", indeterminate=True)
            if stored is None:
                return self._blocked("PROTECTED_BIND", "protected bind absent from durable claim store", indeterminate=True)
            stored_bind, _status = stored
            if stored_bind != bind:
                return self._blocked("PROTECTED_BIND", "durable bind payload differs from supplied bind")
            try:
                claimed = self.bind_store.claim(bind.bind_id, now.isoformat())
            except Exception:
                return self._blocked("PROTECTED_BIND", "durable bind claim state unavailable", indeterminate=True)
            if not claimed:
                return self._blocked("PROTECTED_BIND", "protected bind replay rejected by durable claim store")
            return None

        with self._bind_lock:
            if bind.bind_id in self._claimed_bind_ids:
                return self._blocked("PROTECTED_BIND", "protected bind replay rejected")
            self._claimed_bind_ids.add(bind.bind_id)
        return None

    def execute(self, *, context: WholeStackAuthorityContext, supplied_profile: DeploymentBoundaryProfile,
                route_id: str, target_capability: str, commit: ExactClinicalCommit,
                bind: ProtectedClinicalBind | None, original_decision: str,
                control_contract_version: str, now: datetime,
                break_glass: BreakGlassAuthority | None = None) -> WholeStackEvidence:
        if now.tzinfo is None or now.utcoffset() is None:
            return self._blocked("TRUSTED_TIME", "execution time must be timezone-aware", indeterminate=True)
        effective_now = now.astimezone(timezone.utc)

        critical_commit_identity = {
            "schema_version": commit.schema_version,
            "commit_id": commit.commit_id,
            "patient_ref": commit.patient_ref,
            "encounter_ref": commit.encounter_ref,
            "consultation_ref": commit.consultation_ref,
            "clinician_ref": commit.clinician_ref,
            "document_type": commit.document_type,
            "document_content": commit.document_content,
            "execution_type": commit.execution_type,
            "target_system": commit.target_system,
            "target_instance": commit.target_instance,
            "target_record_ref": commit.target_record_ref,
            "product_identifier": commit.product_identifier,
            "product_version": commit.product_version,
            "workflow_context": commit.workflow_context,
            "intended_use": commit.intended_use,
            "runtime_policy_version": commit.runtime_policy_version,
            "rule_catalogue_version": commit.rule_catalogue_version,
            "materiality_profile": commit.materiality_profile,
            "canonicalisation_profile": commit.canonicalisation_profile,
        }
        invalid_commit_identity = [name for name, value in critical_commit_identity.items() if not _nonblank(value)]
        if invalid_commit_identity:
            return self._blocked(
                "CONSEQUENCE_IDENTITY",
                f"exact consequence identity invalid: {','.join(invalid_commit_identity)}",
            )

        identity_values = (
            context.distributed_deployment_id, context.recovery_deployment_id,
            context.evidence_deployment_id, context.policy_deployment_id,
            context.evidence_subject_ref, context.evidence_product_identifier,
            context.evidence_product_version, context.authority_commit_binding_hash,
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

        required_layers = set(EXPECTED_LAYER_PRODUCERS)
        if not context.layer_evidence:
            return self._blocked("COMPOSITION_EVIDENCE", "layer authority evidence absent", indeterminate=True)
        names = [e.layer for e in context.layer_evidence]
        if len(names) != len(set(names)):
            return self._blocked("COMPOSITION_EVIDENCE", "duplicate layer authority evidence")
        if set(names) != required_layers:
            return self._blocked("COMPOSITION_EVIDENCE", "required layer authority evidence incomplete", indeterminate=True)

        expected_statuses = {
            "DISTRIBUTED_AUTHORITY": context.distributed_status or "ABSENT",
            "RECOVERY_AUTHORITY": context.recovery_authority_status or "ABSENT",
            "EVIDENCE_CONTRACT": context.evidence_contract_status or "ABSENT",
            "POLICY_TRANSITION": context.policy_status or "ABSENT",
            "PRESENT_STANDING": context.present_standing_status or "ABSENT",
        }
        if not isinstance(context.distributed_lease_id, str) or not context.distributed_lease_id.strip():
            return self._blocked("COMPOSITION_EVIDENCE", "current distributed lease identity invalid", indeterminate=True)
        if type(context.distributed_authority_epoch) is not int or context.distributed_authority_epoch <= 0:
            return self._blocked("DISTRIBUTED_AUTHORITY", "distributed authority epoch must be a positive integer")
        if type(context.current_distributed_epoch) is not int or context.current_distributed_epoch <= 0:
            return self._blocked("DISTRIBUTED_AUTHORITY", "current distributed authority epoch must be a positive integer")

        for evidence in context.layer_evidence:
            if evidence.producer_id != EXPECTED_LAYER_PRODUCERS[evidence.layer]:
                return self._blocked("COMPOSITION_EVIDENCE", f"untrusted producer for {evidence.layer}")
            if not verify_layer_authority_evidence(evidence):
                return self._blocked("COMPOSITION_EVIDENCE", f"integrity failure for {evidence.layer}")
            if evidence.deployment_id != expected_deployment:
                return self._blocked("COMPOSITION_EVIDENCE", f"deployment mismatch for {evidence.layer}")
            if evidence.commit_binding_hash != commit.commit_binding_hash:
                return self._blocked("COMPOSITION_EVIDENCE", f"consequence binding mismatch for {evidence.layer}")
            if evidence.status != expected_statuses[evidence.layer]:
                return self._blocked("COMPOSITION_EVIDENCE", f"status disagreement for {evidence.layer}")

            version_dimensions = (
                evidence.authority_epoch, evidence.authority_lease_id,
                evidence.runtime_policy_version, evidence.rule_catalogue_version,
                evidence.control_contract_version, evidence.deployment_profile_version,
            )
            if any(value is None for value in version_dimensions):
                return self._blocked("COMPOSITION_EVIDENCE", f"fencing/version binding absent for {evidence.layer}", indeterminate=True)
            if type(evidence.authority_epoch) is not int or evidence.authority_epoch <= 0:
                return self._blocked("COMPOSITION_EVIDENCE", f"invalid authority epoch type/value for {evidence.layer}")
            if not isinstance(evidence.authority_lease_id, str) or not evidence.authority_lease_id.strip():
                return self._blocked("COMPOSITION_EVIDENCE", f"invalid authority lease identity for {evidence.layer}")
            if type(evidence.deployment_profile_version) is not int or evidence.deployment_profile_version <= 0:
                return self._blocked("COMPOSITION_EVIDENCE", f"invalid deployment profile version type/value for {evidence.layer}")
            if evidence.authority_epoch != context.current_distributed_epoch:
                return self._blocked("COMPOSITION_EVIDENCE", f"authority epoch mismatch for {evidence.layer}")
            if evidence.authority_lease_id != context.distributed_lease_id:
                return self._blocked("COMPOSITION_EVIDENCE", f"authority lease mismatch for {evidence.layer}")
            if evidence.runtime_policy_version != context.authority_policy_version:
                return self._blocked("COMPOSITION_EVIDENCE", f"runtime policy mismatch for {evidence.layer}")
            if evidence.rule_catalogue_version != context.authority_rule_catalogue_version:
                return self._blocked("COMPOSITION_EVIDENCE", f"rule catalogue mismatch for {evidence.layer}")
            if evidence.control_contract_version != control_contract_version:
                return self._blocked("COMPOSITION_EVIDENCE", f"control contract mismatch for {evidence.layer}")
            if evidence.deployment_profile_version != self.enforcer.active_profile.profile_version:
                return self._blocked("COMPOSITION_EVIDENCE", f"deployment profile version mismatch for {evidence.layer}")

            try:
                observed_at = _parse_ts(evidence.observed_at)
            except Exception:
                return self._blocked("COMPOSITION_EVIDENCE", f"invalid observation time for {evidence.layer}", indeterminate=True)
            age = (effective_now - observed_at).total_seconds()
            if age < 0:
                return self._blocked("COMPOSITION_EVIDENCE", f"future observation for {evidence.layer}")
            if age > COMPOSITION_EVIDENCE_MAX_AGE_SECONDS:
                return self._blocked("COMPOSITION_EVIDENCE", f"stale observation for {evidence.layer}")

        if context.distributed_status is None:
            return self._blocked("DISTRIBUTED_AUTHORITY", "distributed authority result absent", indeterminate=True)
        if context.distributed_status == "INDETERMINATE":
            return self._blocked("DISTRIBUTED_AUTHORITY", "distributed authority indeterminate", indeterminate=True)
        if context.distributed_status != "ACTIVE":
            return self._blocked("DISTRIBUTED_AUTHORITY", f"distributed authority not active: {context.distributed_status}")
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

        if commit.runtime_policy_version != context.authority_policy_version:
            return self._blocked("POLICY_BINDING", "exact commit policy basis differs from authority context")
        if commit.rule_catalogue_version != context.authority_rule_catalogue_version:
            return self._blocked("POLICY_BINDING", "exact commit rule catalogue differs from authority context")

        if original_decision == "ALLOW":
            if bind is None:
                return self._blocked("PROTECTED_BIND", "ALLOW path missing protected bind")
            try:
                issued_at = _parse_ts(bind.issued_at)
                expires_at = _parse_ts(bind.expires_at)
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
            if not verify_bind_integrity(bind):
                return self._blocked("PROTECTED_BIND", "protected bind integrity invalid")
            if bind.use_semantics != "SINGLE_USE":
                return self._blocked("PROTECTED_BIND", "protected bind use semantics not single-use")
            claim_failure = self._claim_bind(bind, effective_now)
            if claim_failure is not None:
                return claim_failure

        deployment = self.enforcer.enforce(
            supplied_profile=supplied_profile, route_id=route_id,
            target_capability=target_capability, commit=commit, bind=bind,
            original_decision=original_decision,
            control_contract_version=control_contract_version, now=effective_now,
            break_glass=break_glass,
        )
        return WholeStackEvidence(deployment.status, "DEPLOYMENT", deployment.detail, deployment)
