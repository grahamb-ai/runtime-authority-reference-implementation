from dataclasses import replace

from app.hardening.deployment_enforcement import sign_break_glass_authority
from tests.test_asvh_whole_stack_hostile import context, run
from tests.test_asvh_whole_stack_hostile_v10 import signed_bg


def test_ws12_001_signed_break_glass_with_non_single_use_semantics_cannot_form():
    c, bg = signed_bg("BG-WS12-NON-SINGLE")
    non_single = sign_break_glass_authority(replace(bg, single_use=False, integrity_reference=""))
    assert run(context(), c, decision="REFUSE", bg=non_single).status != "FORMED"


def test_ws12_002_non_single_use_authority_cannot_be_replayed_as_open_ended_override():
    c, bg = signed_bg("BG-WS12-REPLAY")
    non_single = sign_break_glass_authority(replace(bg, single_use=False, integrity_reference=""))
    first = run(context(), c, decision="REFUSE", bg=non_single)
    second = run(context(), c, decision="REFUSE", bg=non_single)
    assert first.status != "FORMED"
    assert second.status != "FORMED"


def test_ws12_003_integrity_bound_single_use_break_glass_remains_valid_control():
    c, bg = signed_bg("BG-WS12-CONTROL")
    assert bg.single_use is True
    assert run(context(), c, decision="REFUSE", bg=bg).status == "FORMED"
