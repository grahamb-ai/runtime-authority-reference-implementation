from tests.test_asvh_whole_stack_hostile import context, run
from tests.test_asvh_whole_stack_hostile_v10 import signed_bg


def test_ws17_001_unknown_original_decision_cannot_become_break_glass_authority():
    c, bg = signed_bg("BG-WS17-UNKNOWN")
    assert run(context(), c, decision="UNKNOWN", bg=bg).status != "FORMED"


def test_ws17_002_blank_original_decision_cannot_become_break_glass_authority():
    c, bg = signed_bg("BG-WS17-BLANK")
    assert run(context(), c, decision="", bg=bg).status != "FORMED"


def test_ws17_003_case_variant_allow_cannot_be_reinterpreted_as_break_glass_path():
    c, bg = signed_bg("BG-WS17-CASE")
    assert run(context(), c, decision="allow", bg=bg).status != "FORMED"


def test_ws17_004_explicit_refuse_with_valid_break_glass_remains_control():
    c, bg = signed_bg("BG-WS17-CONTROL")
    assert run(context(), c, decision="REFUSE", bg=bg).status == "FORMED"
