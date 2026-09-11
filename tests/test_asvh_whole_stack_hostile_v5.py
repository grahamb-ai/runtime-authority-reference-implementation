from dataclasses import replace

from app.hardening.deployment_enforcement import BreakGlassAuthority
from app.hardening.whole_stack import make_layer_authority_evidence
from tests.test_asvh_whole_stack_hostile import NOW, context, run, valid_bind


def _replace_layer(ctx, layer_name, new_evidence):
    return replace(ctx, layer_evidence=tuple(new_evidence if e.layer == layer_name else e for e in ctx.layer_evidence))


def _signed(layer, producer, status, *, epoch=2, lease="LEASE-01", policy="HC-POL-1.0", rules="ASVH-RC-1.0", contract="CC-1.0", profile_version=1):
    c, _ = valid_bind()
    return make_layer_authority_evidence(
        layer=layer,
        producer_id=producer,
        deployment_id="DEP-01",
        commit_binding_hash=c.commit_binding_hash,
        status=status,
        observed_at=NOW.isoformat(),
        authority_epoch=epoch,
        authority_lease_id=lease,
        runtime_policy_version=policy,
        rule_catalogue_version=rules,
        control_contract_version=contract,
        deployment_profile_version=profile_version,
    )


def _legacy_signed(layer, producer, status):
    c, _ = valid_bind()
    return make_layer_authority_evidence(
        layer=layer,
        producer_id=producer,
        deployment_id="DEP-01",
        commit_binding_hash=c.commit_binding_hash,
        status=status,
        observed_at=NOW.isoformat(),
    )


def fully_bound_context():
    ctx = context()
    evidence = (
        _signed("DISTRIBUTED_AUTHORITY", "RA-DISTRIBUTED-01", "ACTIVE"),
        _signed("RECOVERY_AUTHORITY", "RA-RECOVERY-01", "ACTIVE"),
        _signed("EVIDENCE_CONTRACT", "RA-EVIDENCE-01", "ALLOW"),
        _signed("POLICY_TRANSITION", "RA-POLICY-01", "ALLOW"),
        _signed("PRESENT_STANDING", "RA-STANDING-01", "ALLOW"),
    )
    return replace(ctx, layer_evidence=evidence, distributed_lease_id="LEASE-01")


def test_ws5_001_signed_old_epoch_cannot_form():
    ctx = fully_bound_context()
    wrong = _signed("DISTRIBUTED_AUTHORITY", "RA-DISTRIBUTED-01", "ACTIVE", epoch=1)
    assert run(_replace_layer(ctx, "DISTRIBUTED_AUTHORITY", wrong)).status != "FORMED"


def test_ws5_002_signed_wrong_lease_cannot_form():
    ctx = fully_bound_context()
    wrong = _signed("DISTRIBUTED_AUTHORITY", "RA-DISTRIBUTED-01", "ACTIVE", lease="LEASE-OLD")
    assert run(_replace_layer(ctx, "DISTRIBUTED_AUTHORITY", wrong)).status != "FORMED"


def test_ws5_003_signed_wrong_policy_version_cannot_form():
    ctx = fully_bound_context()
    wrong = _signed("POLICY_TRANSITION", "RA-POLICY-01", "ALLOW", policy="HC-POL-0.9")
    assert run(_replace_layer(ctx, "POLICY_TRANSITION", wrong)).status != "FORMED"


def test_ws5_004_signed_wrong_rule_catalogue_cannot_form():
    ctx = fully_bound_context()
    wrong = _signed("POLICY_TRANSITION", "RA-POLICY-01", "ALLOW", rules="ASVH-RC-0.9")
    assert run(_replace_layer(ctx, "POLICY_TRANSITION", wrong)).status != "FORMED"


def test_ws5_005_signed_wrong_control_contract_cannot_form():
    ctx = fully_bound_context()
    wrong = _signed("EVIDENCE_CONTRACT", "RA-EVIDENCE-01", "ALLOW", contract="CC-0.9")
    assert run(_replace_layer(ctx, "EVIDENCE_CONTRACT", wrong)).status != "FORMED"


def test_ws5_006_signed_wrong_deployment_profile_version_cannot_form():
    ctx = fully_bound_context()
    wrong = _signed("PRESENT_STANDING", "RA-STANDING-01", "ALLOW", profile_version=0)
    assert run(_replace_layer(ctx, "PRESENT_STANDING", wrong)).status != "FORMED"


def test_ws5_007_missing_fencing_version_bindings_cannot_form():
    ctx = context()
    legacy = (
        _legacy_signed("DISTRIBUTED_AUTHORITY", "RA-DISTRIBUTED-01", "ACTIVE"),
        _legacy_signed("RECOVERY_AUTHORITY", "RA-RECOVERY-01", "ACTIVE"),
        _legacy_signed("EVIDENCE_CONTRACT", "RA-EVIDENCE-01", "ALLOW"),
        _legacy_signed("POLICY_TRANSITION", "RA-POLICY-01", "ALLOW"),
        _legacy_signed("PRESENT_STANDING", "RA-STANDING-01", "ALLOW"),
    )
    assert run(replace(ctx, layer_evidence=legacy)).status != "FORMED"


def test_ws5_008_break_glass_cannot_bypass_wrong_signed_lease():
    c, _ = valid_bind()
    ctx = fully_bound_context()
    wrong = _signed("DISTRIBUTED_AUTHORITY", "RA-DISTRIBUTED-01", "ACTIVE", lease="LEASE-OLD")
    ctx = _replace_layer(ctx, "DISTRIBUTED_AUTHORITY", wrong)
    bg = BreakGlassAuthority(
        override_id="BG-WS5-1", authority_identity="CLINICAL-DUTY-MANAGER",
        commit_binding_hash=c.commit_binding_hash, deployment_id="DEP-01",
        issued_at="2026-09-11T11:55:00+00:00", expires_at="2026-09-11T12:05:00+00:00",
        policy_version="BG-1.0", single_use=True,
    )
    assert run(ctx, c, decision="REFUSE", bg=bg).status != "FORMED"


def test_ws5_009_fully_bound_current_layer_evidence_can_form():
    assert run(fully_bound_context()).status == "FORMED"
