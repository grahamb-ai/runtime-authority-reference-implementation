import hashlib
import hmac
import json
from dataclasses import replace

from app.hardening.deployment_enforcement import BreakGlassAuthority
from tests.test_asvh_whole_stack_hostile import NOW, context, run, valid_bind

REFERENCE_BREAK_GLASS_KEY = b"asvh-reference-break-glass-only"


def _payload(bg: BreakGlassAuthority) -> str:
    return json.dumps({
        "override_id": bg.override_id,
        "authority_identity": bg.authority_identity,
        "commit_binding_hash": bg.commit_binding_hash,
        "deployment_id": bg.deployment_id,
        "issued_at": bg.issued_at,
        "expires_at": bg.expires_at,
        "policy_version": bg.policy_version,
        "single_use": bg.single_use,
    }, sort_keys=True, separators=(",", ":"))


def signed_bg():
    c, _ = valid_bind()
    unsigned = BreakGlassAuthority(
        override_id="BG-WS9-1",
        authority_identity="CLINICAL-DUTY-MANAGER",
        commit_binding_hash=c.commit_binding_hash,
        deployment_id="DEP-01",
        issued_at="2026-09-11T11:55:00+00:00",
        expires_at="2026-09-11T12:05:00+00:00",
        policy_version="BG-1.0",
        single_use=True,
    )
    digest = hmac.new(REFERENCE_BREAK_GLASS_KEY, _payload(unsigned).encode("utf-8"), hashlib.sha256).hexdigest()
    return c, replace(unsigned, integrity_reference=f"BG-HMAC-SHA256-1:{digest}")


def test_ws9_001_unsigned_break_glass_cannot_form():
    c, signed = signed_bg()
    unsigned = replace(signed, integrity_reference="")
    assert run(context(), c, decision="REFUSE", bg=unsigned).status != "FORMED"


def test_ws9_002_bogus_break_glass_integrity_cannot_form():
    c, signed = signed_bg()
    forged = replace(signed, integrity_reference="BG-HMAC-SHA256-1:deadbeef")
    assert run(context(), c, decision="REFUSE", bg=forged).status != "FORMED"


def test_ws9_003_identity_tamper_after_signature_cannot_form():
    c, signed = signed_bg()
    tampered = replace(signed, authority_identity="UNAUTHORISED-SUBSTITUTE")
    assert run(context(), c, decision="REFUSE", bg=tampered).status != "FORMED"


def test_ws9_004_temporal_tamper_after_signature_cannot_form():
    c, signed = signed_bg()
    tampered = replace(signed, expires_at="2026-09-11T12:06:00+00:00")
    assert run(context(), c, decision="REFUSE", bg=tampered).status != "FORMED"


def test_ws9_005_valid_integrity_bound_break_glass_can_form():
    c, signed = signed_bg()
    assert run(context(), c, decision="REFUSE", bg=signed).status == "FORMED"
