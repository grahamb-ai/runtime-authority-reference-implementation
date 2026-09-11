from dataclasses import replace

from app.hardening.deployment_enforcement import BreakGlassAuthority
from tests.test_asvh_whole_stack_hostile import NOW, context, run, valid_bind


def test_ws2_001_recovery_prevented_cannot_form():
    r = run(replace(context(), recovery_authority_status="PREVENTED", evidence_contract_status="ALLOW"))
    assert r.status != "FORMED"


def test_ws2_002_recovery_indeterminate_cannot_form():
    r = run(replace(context(), recovery_authority_status="INDETERMINATE", evidence_contract_status="ALLOW"))
    assert r.status != "FORMED"


def test_ws2_003_missing_recovery_result_cannot_form():
    r = run(replace(context(), recovery_authority_status=None, evidence_contract_status="ALLOW"))
    assert r.status != "FORMED"


def test_ws2_004_evidence_refuse_cannot_form():
    r = run(replace(context(), recovery_authority_status="ACTIVE", evidence_contract_status="REFUSE"))
    assert r.status != "FORMED"


def test_ws2_005_evidence_escalate_cannot_form():
    r = run(replace(context(), recovery_authority_status="ACTIVE", evidence_contract_status="ESCALATE"))
    assert r.status != "FORMED"


def test_ws2_006_missing_evidence_result_cannot_form():
    r = run(replace(context(), recovery_authority_status="ACTIVE", evidence_contract_status=None))
    assert r.status != "FORMED"


def test_ws2_007_recovery_failure_is_decisive_even_with_break_glass():
    c, _ = valid_bind()
    bg = BreakGlassAuthority(
        override_id="BG-WS2-1", authority_identity="CLINICAL-DUTY-MANAGER",
        commit_binding_hash=c.commit_binding_hash, deployment_id="DEP-01",
        issued_at="2026-09-11T11:55:00+00:00", expires_at="2026-09-11T12:05:00+00:00",
        policy_version="BG-1.0", single_use=True,
    )
    ctx = replace(context(), recovery_authority_status="PREVENTED", evidence_contract_status="ALLOW")
    r = run(ctx, c, decision="REFUSE", bg=bg)
    assert r.status != "FORMED" and r.decisive_layer == "RECOVERY_AUTHORITY"


def test_ws2_008_evidence_failure_is_decisive_even_with_break_glass():
    c, _ = valid_bind()
    bg = BreakGlassAuthority(
        override_id="BG-WS2-2", authority_identity="CLINICAL-DUTY-MANAGER",
        commit_binding_hash=c.commit_binding_hash, deployment_id="DEP-01",
        issued_at="2026-09-11T11:55:00+00:00", expires_at="2026-09-11T12:05:00+00:00",
        policy_version="BG-1.0", single_use=True,
    )
    ctx = replace(context(), recovery_authority_status="ACTIVE", evidence_contract_status="REFUSE")
    r = run(ctx, c, decision="REFUSE", bg=bg)
    assert r.status != "FORMED" and r.decisive_layer == "EVIDENCE_CONTRACT"
