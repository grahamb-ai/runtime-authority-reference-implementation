from dataclasses import replace

from app.hardening.deployment_enforcement import BreakGlassAuthority
from tests.test_asvh_whole_stack_hostile import NOW, context, run, valid_bind


def test_ws3_001_distributed_deployment_mismatch_cannot_form():
    r = run(replace(context(), distributed_deployment_id="DEP-OTHER"))
    assert r.status != "FORMED"


def test_ws3_002_recovery_deployment_mismatch_cannot_form():
    r = run(replace(context(), recovery_deployment_id="DEP-OTHER"))
    assert r.status != "FORMED"


def test_ws3_003_evidence_deployment_mismatch_cannot_form():
    r = run(replace(context(), evidence_deployment_id="DEP-OTHER"))
    assert r.status != "FORMED"


def test_ws3_004_policy_deployment_mismatch_cannot_form():
    r = run(replace(context(), policy_deployment_id="DEP-OTHER"))
    assert r.status != "FORMED"


def test_ws3_005_evidence_subject_mismatch_cannot_form():
    r = run(replace(context(), evidence_subject_ref="PAT-OTHER"))
    assert r.status != "FORMED"


def test_ws3_006_evidence_product_mismatch_cannot_form():
    r = run(replace(context(), evidence_product_identifier="AVT-OTHER"))
    assert r.status != "FORMED"


def test_ws3_007_evidence_product_version_mismatch_cannot_form():
    r = run(replace(context(), evidence_product_version="9.9.9"))
    assert r.status != "FORMED"


def test_ws3_008_authority_consequence_hash_mismatch_cannot_form():
    r = run(replace(context(), authority_commit_binding_hash="sha256:deadbeef"))
    assert r.status != "FORMED"


def test_ws3_009_missing_identity_binding_is_indeterminate():
    r = run(replace(context(), evidence_subject_ref=None))
    assert r.status == "INDETERMINATE"


def test_ws3_010_break_glass_cannot_bypass_identity_mismatch():
    c, _ = valid_bind()
    bg = BreakGlassAuthority(
        override_id="BG-WS3-1",
        authority_identity="CLINICAL-DUTY-MANAGER",
        commit_binding_hash=c.commit_binding_hash,
        deployment_id="DEP-01",
        issued_at="2026-09-11T11:55:00+00:00",
        expires_at="2026-09-11T12:05:00+00:00",
        policy_version="BG-1.0",
        single_use=True,
    )
    ctx = replace(context(), evidence_subject_ref="PAT-OTHER")
    r = run(ctx, c, decision="REFUSE", bg=bg, now=NOW)
    assert r.status != "FORMED"


def test_ws3_011_all_identity_dimensions_coherent_can_form():
    r = run(context())
    assert r.status == "FORMED"
