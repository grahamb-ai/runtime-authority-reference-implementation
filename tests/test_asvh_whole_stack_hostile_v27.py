from dataclasses import replace

from app.hardening.deployment_enforcement import DeploymentBoundaryProfile, DeploymentEnforcer, RouteBinding
from app.hardening.whole_stack import WholeStackAuthorityContext, WholeStackExecutionCoordinator, make_layer_authority_evidence
from tests.test_asvh_harden_001 import baseline_commit
from tests.test_asvh_whole_stack_hostile import NOW, profile, valid_bind


def _run_with_profile(p: DeploymentBoundaryProfile, *, route_id="EPR-COMMIT", target_capability="EPR_WRITE", contract="CC-1.0"):
    c, b = valid_bind(baseline_commit())
    observed_at = NOW.isoformat()
    common = dict(
        deployment_id=p.deployment_id,
        commit_binding_hash=c.commit_binding_hash,
        observed_at=observed_at,
        authority_epoch=2,
        authority_lease_id="LEASE-01",
        runtime_policy_version=c.runtime_policy_version,
        rule_catalogue_version=c.rule_catalogue_version,
        control_contract_version=contract,
        deployment_profile_version=p.profile_version,
    )
    layer_evidence = (
        make_layer_authority_evidence(layer="DISTRIBUTED_AUTHORITY", producer_id="RA-DISTRIBUTED-01", status="ACTIVE", **common),
        make_layer_authority_evidence(layer="RECOVERY_AUTHORITY", producer_id="RA-RECOVERY-01", status="ACTIVE", **common),
        make_layer_authority_evidence(layer="EVIDENCE_CONTRACT", producer_id="RA-EVIDENCE-01", status="ALLOW", **common),
        make_layer_authority_evidence(layer="POLICY_TRANSITION", producer_id="RA-POLICY-01", status="ALLOW", **common),
        make_layer_authority_evidence(layer="PRESENT_STANDING", producer_id="RA-STANDING-01", status="ALLOW", **common),
    )
    ctx = WholeStackAuthorityContext(
        distributed_status="ACTIVE", policy_status="ALLOW", present_standing_status="ALLOW",
        authority_policy_version=c.runtime_policy_version,
        authority_rule_catalogue_version=c.rule_catalogue_version,
        distributed_authority_epoch=2, current_distributed_epoch=2, distributed_lease_id="LEASE-01",
        recovery_authority_status="ACTIVE", evidence_contract_status="ALLOW",
        distributed_deployment_id=p.deployment_id, recovery_deployment_id=p.deployment_id,
        evidence_deployment_id=p.deployment_id, policy_deployment_id=p.deployment_id,
        evidence_subject_ref=c.patient_ref, evidence_product_identifier=c.product_identifier,
        evidence_product_version=c.product_version, authority_commit_binding_hash=c.commit_binding_hash,
        layer_evidence=layer_evidence,
    )
    coord = WholeStackExecutionCoordinator(DeploymentEnforcer(p))
    return coord.execute(
        context=ctx, supplied_profile=p, route_id=route_id, target_capability=target_capability,
        commit=c, bind=b, original_decision="ALLOW", control_contract_version=contract, now=NOW,
    )


def test_ws27_001_blank_deployment_identity_cannot_form():
    p = replace(profile(), deployment_id="")
    assert _run_with_profile(p).status != "FORMED"


def test_ws27_002_blank_profile_identity_cannot_form():
    p = replace(profile(), profile_id="   ")
    assert _run_with_profile(p).status != "FORMED"


def test_ws27_003_blank_control_contract_cannot_form():
    p = replace(profile(), active_control_contract_version="")
    assert _run_with_profile(p, contract="").status != "FORMED"


def test_ws27_004_blank_governed_consequence_type_cannot_form():
    p = replace(profile(), governed_consequence_type="")
    assert _run_with_profile(p).status != "FORMED"


def test_ws27_005_blank_route_identity_cannot_form():
    p = replace(profile(), protected_routes=(RouteBinding("", "EPR_WRITE"),))
    assert _run_with_profile(p, route_id="").status != "FORMED"


def test_ws27_006_blank_target_capability_cannot_form():
    p = replace(profile(), protected_routes=(RouteBinding("EPR-COMMIT", ""),))
    assert _run_with_profile(p, target_capability="").status != "FORMED"


def test_ws27_007_valid_control_still_forms():
    assert _run_with_profile(profile()).status == "FORMED"
