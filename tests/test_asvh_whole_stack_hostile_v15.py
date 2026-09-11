from dataclasses import replace
from datetime import datetime

from app.hardening.deployment_enforcement import sign_break_glass_authority
from tests.test_asvh_whole_stack_hostile import context, run
from tests.test_asvh_whole_stack_hostile_v10 import signed_bg


def _resign(bg, **changes):
    hostile = replace(bg, integrity_reference="", **changes)
    return sign_break_glass_authority(hostile)


def test_ws15_001_naive_issued_at_fails_closed_without_exception():
    c, bg = signed_bg("BG-WS15-NAIVE-ISSUED")
    hostile = _resign(bg, issued_at="2026-09-11T11:55:00")
    assert run(context(), c, decision="REFUSE", bg=hostile).status != "FORMED"


def test_ws15_002_naive_expires_at_fails_closed_without_exception():
    c, bg = signed_bg("BG-WS15-NAIVE-EXPIRES")
    hostile = _resign(bg, expires_at="2026-09-11T12:05:00")
    assert run(context(), c, decision="REFUSE", bg=hostile).status != "FORMED"


def test_ws15_003_naive_execution_time_fails_closed_without_exception():
    c, bg = signed_bg("BG-WS15-NAIVE-NOW")
    naive_now = datetime(2026, 9, 11, 12, 0, 0)
    assert run(context(), c, decision="REFUSE", bg=bg, now=naive_now).status != "FORMED"


def test_ws15_004_timezone_aware_control_remains_valid():
    c, bg = signed_bg("BG-WS15-CONTROL")
    assert run(context(), c, decision="REFUSE", bg=bg).status == "FORMED"
