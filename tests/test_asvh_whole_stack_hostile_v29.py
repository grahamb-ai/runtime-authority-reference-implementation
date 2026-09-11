from dataclasses import replace

from tests.test_asvh_whole_stack_hostile import profile
from tests.test_asvh_whole_stack_hostile_v27 import _run_with_profile


def test_ws29_001_integer_profile_integrity_flag_cannot_form():
    p = replace(profile(), integrity_valid=1)
    assert _run_with_profile(p).status != "FORMED"


def test_ws29_002_string_profile_integrity_flag_cannot_form():
    p = replace(profile(), integrity_valid="true")
    assert _run_with_profile(p).status != "FORMED"


def test_ws29_003_false_profile_integrity_flag_remains_prevented():
    p = replace(profile(), integrity_valid=False)
    assert _run_with_profile(p).status != "FORMED"


def test_ws29_004_exact_true_profile_integrity_control_forms():
    assert _run_with_profile(profile()).status == "FORMED"
