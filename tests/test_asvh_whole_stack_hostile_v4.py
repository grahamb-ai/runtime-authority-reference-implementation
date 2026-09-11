from dataclasses import replace
from datetime import timedelta

from app.hardening.deployment_enforcement import BreakGlassAuthority
from app.hardening.whole_stack import make_layer_authority_evidence
from tests.test_asvh_whole_stack_hostile import NOW, context, run, valid_bind


def _replace_layer(ctx, layer_name, new_evidence):
    return replace(ctx, layer_evidence=tuple(new_evidence if e.layer == layer_name else e for e in ctx.layer_evidence))


def test_ws4_001_missing_layer_evidence_cannot_form():
    r = run(replace(context(), layer_evidence=()))
    assert r.status != "FORMED"


def test_ws4_002_forged_layer_integrity_cannot_form():
    ctx = context()
    e = ctx.layer_evidence[0]
    forged = replace(e, integrity_reference="WS-HMAC-SHA256-1:deadbeef")
    r = run(_replace_layer(ctx, e.layer, forged))
    assert r.status != "FORMED"


def test_ws4_003_signed_status_disagrees_with_context_cannot_form():
    ctx = context()
    c, _ = valid_bind()
    contradictory = make_layer_authority_evidence(
        layer="EVIDENCE_CONTRACT", producer_id="RA-EVIDENCE-01", deployment_id="DEP-01",
        commit_binding_hash=c.commit_binding_hash, status="REFUSE", observed_at=NOW.isoformat(),
    )
    r = run(_replace_layer(ctx, "EVIDENCE_CONTRACT", contradictory))
    assert r.status != "FORMED"


def test_ws4_004_missing_required_layer_among_other_valid_layers_cannot_form():
    ctx = context()
    r = run(replace(ctx, layer_evidence=tuple(e for e in ctx.layer_evidence if e.layer != "POLICY_TRANSITION")))
    assert r.status != "FORMED"


def test_ws4_005_duplicate_layer_shadowing_cannot_form():
    ctx = context()
    duplicate = ctx.layer_evidence[0]
    r = run(replace(ctx, layer_evidence=ctx.layer_evidence + (duplicate,)))
    assert r.status != "FORMED"


def test_ws4_006_authorised_layer_producer_substitution_cannot_form():
    ctx = context()
    c, _ = valid_bind()
    substituted = make_layer_authority_evidence(
        layer="RECOVERY_AUTHORITY", producer_id="REQUESTING_AI", deployment_id="DEP-01",
        commit_binding_hash=c.commit_binding_hash, status="ACTIVE", observed_at=NOW.isoformat(),
    )
    r = run(_replace_layer(ctx, "RECOVERY_AUTHORITY", substituted))
    assert r.status != "FORMED"


def test_ws4_007_signed_wrong_consequence_binding_cannot_form():
    ctx = context()
    wrong = make_layer_authority_evidence(
        layer="PRESENT_STANDING", producer_id="RA-STANDING-01", deployment_id="DEP-01",
        commit_binding_hash="sha256:other", status="ALLOW", observed_at=NOW.isoformat(),
    )
    r = run(_replace_layer(ctx, "PRESENT_STANDING", wrong))
    assert r.status != "FORMED"


def test_ws4_008_signed_stale_composition_evidence_cannot_form():
    ctx = context()
    c, _ = valid_bind()
    stale = make_layer_authority_evidence(
        layer="DISTRIBUTED_AUTHORITY", producer_id="RA-DISTRIBUTED-01", deployment_id="DEP-01",
        commit_binding_hash=c.commit_binding_hash, status="ACTIVE", observed_at=(NOW - timedelta(seconds=31)).isoformat(),
    )
    r = run(_replace_layer(ctx, "DISTRIBUTED_AUTHORITY", stale))
    assert r.status != "FORMED"


def test_ws4_009_future_composition_evidence_cannot_form():
    ctx = context()
    c, _ = valid_bind()
    future = make_layer_authority_evidence(
        layer="POLICY_TRANSITION", producer_id="RA-POLICY-01", deployment_id="DEP-01",
        commit_binding_hash=c.commit_binding_hash, status="ALLOW", observed_at=(NOW + timedelta(seconds=1)).isoformat(),
    )
    r = run(_replace_layer(ctx, "POLICY_TRANSITION", future))
    assert r.status != "FORMED"


def test_ws4_010_break_glass_cannot_bypass_layer_evidence_integrity():
    c, _ = valid_bind()
    ctx = context()
    evidence = ctx.layer_evidence[2]
    forged = replace(evidence, integrity_reference="WS-HMAC-SHA256-1:deadbeef")
    ctx = _replace_layer(ctx, "EVIDENCE_CONTRACT", forged)
    bg = BreakGlassAuthority(
        override_id="BG-WS4-1", authority_identity="CLINICAL-DUTY-MANAGER",
        commit_binding_hash=c.commit_binding_hash, deployment_id="DEP-01",
        issued_at="2026-09-11T11:55:00+00:00", expires_at="2026-09-11T12:05:00+00:00",
        policy_version="BG-1.0", single_use=True,
    )
    r = run(ctx, c, decision="REFUSE", bg=bg)
    assert r.status != "FORMED"


def test_ws4_011_valid_integrity_bound_layer_evidence_can_form():
    assert run(context()).status == "FORMED"
