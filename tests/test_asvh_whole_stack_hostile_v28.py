from dataclasses import replace

from app.hardening.deployment_enforcement import BreakGlassAuthority
from tests.test_asvh_whole_stack_hostile import NOW, context, run, valid_bind


def test_ws28_001_non_string_layer_integrity_reference_fails_closed():
    ctx = context()
    malformed = (replace(ctx.layer_evidence[0], integrity_reference=1),) + ctx.layer_evidence[1:]
    hostile = replace(ctx, layer_evidence=malformed)
    assert run(hostile).status != "FORMED"


def test_ws28_002_none_layer_integrity_reference_fails_closed():
    ctx = context()
    malformed = (replace(ctx.layer_evidence[0], integrity_reference=None),) + ctx.layer_evidence[1:]
    hostile = replace(ctx, layer_evidence=malformed)
    assert run(hostile).status != "FORMED"


def test_ws28_003_non_string_bind_integrity_reference_fails_closed():
    c, b = valid_bind()
    malformed = replace(b, integrity_reference=1)
    assert run(context(), c, malformed).status != "FORMED"


def test_ws28_004_non_string_break_glass_integrity_reference_fails_closed():
    c, _ = valid_bind()
    bg = BreakGlassAuthority(
        override_id="BG-WS28", authority_identity="CLINICAL-DUTY-MANAGER",
        commit_binding_hash=c.commit_binding_hash, deployment_id="DEP-01",
        issued_at="2026-09-11T11:55:00+00:00", expires_at="2026-09-11T12:05:00+00:00",
        policy_version="BG-1.0", single_use=True, integrity_reference=1,
    )
    assert run(context(), c, decision="REFUSE", bg=bg, now=NOW).status != "FORMED"


def test_ws28_005_valid_control_still_forms():
    assert run(context()).status == "FORMED"
