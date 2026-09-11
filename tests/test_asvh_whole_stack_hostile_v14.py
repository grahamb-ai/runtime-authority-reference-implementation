from dataclasses import replace

from app.hardening.deployment_enforcement import sign_break_glass_authority
from tests.test_asvh_whole_stack_hostile import context, run
from tests.test_asvh_whole_stack_hostile_v10 import signed_bg


def _resign(bg, **changes):
    hostile = replace(bg, integrity_reference="", **changes)
    return sign_break_glass_authority(hostile)


def test_ws14_001_excessively_long_future_validity_window_cannot_form():
    c, bg = signed_bg("BG-WS14-LONG-FUTURE")
    hostile = _resign(bg, expires_at="2026-09-12T12:00:00+00:00")
    assert run(context(), c, decision="REFUSE", bg=hostile).status != "FORMED"


def test_ws14_002_backdated_open_window_cannot_form_even_if_current_now():
    c, bg = signed_bg("BG-WS14-BACKDATED")
    hostile = _resign(
        bg,
        issued_at="2026-09-10T12:00:00+00:00",
        expires_at="2026-09-11T12:05:00+00:00",
    )
    assert run(context(), c, decision="REFUSE", bg=hostile).status != "FORMED"


def test_ws14_003_very_long_window_spanning_now_cannot_form():
    c, bg = signed_bg("BG-WS14-SPAN")
    hostile = _resign(
        bg,
        issued_at="2026-09-10T00:00:00+00:00",
        expires_at="2026-09-13T00:00:00+00:00",
    )
    assert run(context(), c, decision="REFUSE", bg=hostile).status != "FORMED"


def test_ws14_004_short_integrity_bound_window_remains_valid_control():
    c, bg = signed_bg("BG-WS14-CONTROL")
    assert run(context(), c, decision="REFUSE", bg=bg).status == "FORMED"
