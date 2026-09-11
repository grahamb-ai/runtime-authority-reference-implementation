from dataclasses import replace

from app.hardening.deployment_enforcement import sign_break_glass_authority
from tests.test_asvh_whole_stack_hostile import context, run
from tests.test_asvh_whole_stack_hostile_v10 import signed_bg


def _resign(bg, **changes):
    return sign_break_glass_authority(replace(bg, integrity_reference="", **changes))


def test_ws13_001_whitespace_only_authority_identity_cannot_form():
    c, bg = signed_bg("BG-WS13-IDENTITY")
    hostile = _resign(bg, authority_identity="   ")
    assert run(context(), c, decision="REFUSE", bg=hostile).status != "FORMED"


def test_ws13_002_empty_override_identifier_cannot_form():
    c, bg = signed_bg("BG-WS13-EMPTY-ID")
    hostile = _resign(bg, override_id="")
    assert run(context(), c, decision="REFUSE", bg=hostile).status != "FORMED"


def test_ws13_003_whitespace_only_override_identifier_cannot_form():
    c, bg = signed_bg("BG-WS13-SPACE-ID")
    hostile = _resign(bg, override_id="   ")
    assert run(context(), c, decision="REFUSE", bg=hostile).status != "FORMED"


def test_ws13_004_well_formed_integrity_bound_break_glass_remains_valid_control():
    c, bg = signed_bg("BG-WS13-CONTROL")
    assert bg.authority_identity.strip()
    assert bg.override_id.strip()
    assert run(context(), c, decision="REFUSE", bg=bg).status == "FORMED"
