from dataclasses import replace

from app.hardening.deployment_enforcement import sign_break_glass_authority
from tests.test_asvh_whole_stack_hostile import context, run
from tests.test_asvh_whole_stack_hostile_v10 import signed_bg


def _resign(bg, **changes):
    hostile = replace(bg, integrity_reference="", **changes)
    return sign_break_glass_authority(hostile)


def test_ws16_001_unknown_break_glass_authority_identity_cannot_form():
    c, bg = signed_bg("BG-WS16-UNKNOWN")
    hostile = _resign(bg, authority_identity="ANY-AUTHENTICATED-USER")
    assert run(context(), c, decision="REFUSE", bg=hostile).status != "FORMED"


def test_ws16_002_case_variant_authority_identity_cannot_form():
    c, bg = signed_bg("BG-WS16-CASE")
    hostile = _resign(bg, authority_identity="clinical-duty-manager")
    assert run(context(), c, decision="REFUSE", bg=hostile).status != "FORMED"


def test_ws16_003_whitespace_variant_authority_identity_cannot_form():
    c, bg = signed_bg("BG-WS16-WHITESPACE")
    hostile = _resign(bg, authority_identity="CLINICAL-DUTY-MANAGER ")
    assert run(context(), c, decision="REFUSE", bg=hostile).status != "FORMED"


def test_ws16_004_exact_authorised_identity_remains_valid_control():
    c, bg = signed_bg("BG-WS16-CONTROL")
    assert bg.authority_identity == "CLINICAL-DUTY-MANAGER"
    assert run(context(), c, decision="REFUSE", bg=bg).status == "FORMED"
