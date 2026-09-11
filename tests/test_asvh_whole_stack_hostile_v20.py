from datetime import datetime

from tests.test_asvh_whole_stack_hostile import context, run


def test_ws20_001_naive_execution_time_cannot_form_ordinary_allow_consequence():
    naive_now = datetime(2026, 9, 11, 12, 0, 0)
    assert run(context(), now=naive_now).status != "FORMED"


def test_ws20_002_timezone_aware_execution_time_remains_valid_control():
    assert run(context()).status == "FORMED"
