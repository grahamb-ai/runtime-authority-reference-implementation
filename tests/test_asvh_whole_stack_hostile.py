from dataclasses import replace
from datetime import datetime, timezone

from app.hardening.deployment_enforcement import (
    BreakGlassAuthority, DeploymentBoundaryProfile, DeploymentEnforcer, RouteBinding,
)
from app.hardening.runtime import HarnessClock, make_authority_receipt, make_protected_bind
from app.hardening.whole_stack import (
    WholeStackAuthorityContext,
    WholeStackExecutionCoordinator,
    make_layer_authority_evidence,
)
from tests.test_asvh_harden_001 import baseline_commit

NOW = datetime(2026, 9, 11, 12, 0, tzinfo=timezone.utc)


def profile():
    return DeploymentBoundaryProfile(
        profile_id="HC-DEPLOY-01",
        profile_version=1,
        deployment_id="DEP-01",
        governed_consequence_type="EPR_COMMIT",
        active_control_contract_version="CC-1.0",
        protected_routes=(RouteBinding("EPR-COMMIT", "EPR_WRITE"),),
        break_glass_policy_version="BG-1.0",
    )


def valid_bind(commit=None):
    commit = commit or baseline_commit()
    clock = HarnessClock(NOW)
    receipt = make_authority_receipt("ALLOW", commit, clock)
    bind = make_protected_bind(receipt, commit, clock)
    assert bind is not None
    return commit, bind


def _layer_evidence(c, distributed, recovery, evidence, policy, standing):
    observed_at = NOW.isoformat()
    return (
        make_layer_authority_evidence(layer="DISTRIBUTED_AUTHORITY", producer_id="RA-DISTRIBUTED-01", deployment_id="DEP-01", commit_binding_hash=c.commit_binding_hash, status=distributed or "ABSENT", observed_at=observed_at),
        make_layer_authority_evidence(layer="RECOVERY_AUTHORITY", producer_id="RA-RECOVERY-01", deployment_id="DEP-01", commit_binding_hash=c.commit_binding_hash, status=recovery or "ABSENT", observed_at=observed_at),
        make_layer_authority_evidence(layer="EVIDENCE_CONTRACT", producer_id="RA-EVIDENCE-01", deployment_id="DEP-01", commit_binding_hash=c.commit_binding_hash, status=evidence or "ABSENT", observed_at=observed_at),
        make_layer_authority_evidence(layer="POLICY_TRANSITION", producer_id="RA-POLICY-01", deployment_id="DEP-01", commit_binding_hash=c.commit_binding_hash, status=policy or "ABSENT", observed_at=observed_at),
        make_layer_authority_evidence(layer="PRESENT_STANDING", producer_id="RA-STANDING-01", deployment_id="DEP-01", commit_binding_hash=c.commit_binding_hash, status=standing or "ABSENT", observed_at=observed_at),
    )


def context(distributed="ACTIVE", policy="ALLOW", standing="ALLOW", *, authority_policy="HC-POL-1.0", rules="ASVH-RC-1.0", epoch=2, current_epoch=2, recovery="ACTIVE", evidence="ALLOW"):
    c = baseline_commit()
    return WholeStackAuthorityContext(
        distributed_status=distributed,
        policy_status=policy,
        present_standing_status=standing,
        authority_policy_version=authority_policy,
        authority_rule_catalogue_version=rules,
        distributed_authority_epoch=epoch,
        current_distributed_epoch=current_epoch,
        recovery_authority_status=recovery,
        evidence_contract_status=evidence,
        distributed_deployment_id="DEP-01",
        recovery_deployment_id="DEP-01",
        evidence_deployment_id="DEP-01",
        policy_deployment_id="DEP-01",
        evidence_subject_ref=c.patient_ref,
        evidence_product_identifier=c.product_identifier,
        evidence_product_version=c.product_version,
        authority_commit_binding_hash=c.commit_binding_hash,
        layer_evidence=_layer_evidence(c, distributed, recovery, evidence, policy, standing),
    )


def run(ctx, commit=None, bind=None, decision="ALLOW", bg=None, now=NOW):
    p = profile()
    c, b = valid_bind(commit)
    if bind is not None:
        b = bind
    coord = WholeStackExecutionCoordinator(DeploymentEnforcer(p))
    return coord.execute(
        context=ctx,
        supplied_profile=p,
        route_id="EPR-COMMIT",
        target_capability="EPR_WRITE",
        commit=c,
        bind=b,
        original_decision=decision,
        control_contract_version="CC-1.0",
        now=now,
        break_glass=bg,
    )


def test_ws_001_distributed_prevented_cannot_form():
    assert run(context(distributed="PREVENTED")).status != "FORMED"


def test_ws_002_distributed_indeterminate_cannot_form():
    assert run(context(distributed="INDETERMINATE")).status != "FORMED"


def test_ws_003_policy_invalidate_cannot_form():
    assert run(context(policy="INVALIDATE")).status != "FORMED"


def test_ws_004_policy_revalidate_cannot_form_old_authority():
    assert run(context(policy="REVALIDATE")).status != "FORMED"


def test_ws_005_present_standing_prevented_cannot_form():
    assert run(context(standing="PREVENTED")).status != "FORMED"


def test_ws_006_present_standing_indeterminate_cannot_form():
    assert run(context(standing="INDETERMINATE")).status != "FORMED"


def test_ws_007_expired_bind_cannot_form():
    c, b = valid_bind()
    expired = replace(b, expires_at="2026-09-11T11:59:00+00:00")
    assert run(context(), c, expired).status != "FORMED"


def test_ws_008_bind_policy_basis_mismatch_cannot_form():
    c, b = valid_bind()
    forged = replace(b, runtime_policy_version="HC-POL-0.9")
    assert run(context(), c, forged).status != "FORMED"


def test_ws_009_missing_distributed_result_cannot_form():
    assert run(context(distributed=None)).status != "FORMED"


def test_ws_010_missing_policy_result_cannot_form():
    assert run(context(policy=None)).status != "FORMED"


def test_ws_011_missing_standing_result_cannot_form():
    assert run(context(standing=None)).status != "FORMED"


def test_ws_012_upstream_failure_is_decisive_layer():
    r = run(context(distributed="PREVENTED"))
    assert r.decisive_layer == "DISTRIBUTED_AUTHORITY"


def test_ws_013_newer_distributed_epoch_fences_old_context():
    assert run(context(epoch=1, current_epoch=2)).status != "FORMED"


def test_ws_014_break_glass_does_not_bypass_distributed_fencing():
    c, _ = valid_bind()
    bg = BreakGlassAuthority(
        override_id="BG-1", authority_identity="CLINICAL-DUTY-MANAGER",
        commit_binding_hash=c.commit_binding_hash, deployment_id="DEP-01",
        issued_at="2026-09-11T11:55:00+00:00", expires_at="2026-09-11T12:05:00+00:00",
        policy_version="BG-1.0", single_use=True,
    )
    assert run(context(distributed="PREVENTED"), c, decision="REFUSE", bg=bg).status != "FORMED"


def test_ws_015_break_glass_does_not_bypass_incompatible_policy_transition():
    c, _ = valid_bind()
    bg = BreakGlassAuthority(
        override_id="BG-2", authority_identity="CLINICAL-DUTY-MANAGER",
        commit_binding_hash=c.commit_binding_hash, deployment_id="DEP-01",
        issued_at="2026-09-11T11:55:00+00:00", expires_at="2026-09-11T12:05:00+00:00",
        policy_version="BG-1.0", single_use=True,
    )
    assert run(context(policy="INVALIDATE"), c, decision="REFUSE", bg=bg).status != "FORMED"


def test_ws_016_superseded_policy_basis_requires_fresh_authority():
    c, b = valid_bind()
    newer_commit = replace(c, runtime_policy_version="HC-POL-1.1")
    assert run(context(authority_policy="HC-POL-1.0"), newer_commit, b).status != "FORMED"
