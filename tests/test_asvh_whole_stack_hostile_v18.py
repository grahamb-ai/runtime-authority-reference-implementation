from datetime import datetime, timedelta

from tests.test_asvh_whole_stack_hostile import context, run
from tests.test_asvh_whole_stack_hostile_v10 import signed_bg


def test_ws18_001_break_glass_is_expired_at_exact_expiry_boundary():
    c, bg = signed_bg("BG-WS18-EXPIRY")
    expiry = datetime.fromisoformat(bg.expires_at)
    assert run(context(), c, decision="REFUSE", bg=bg, now=expiry).status != "FORMED"


def test_ws18_002_break_glass_remains_valid_immediately_before_expiry():
    c, bg = signed_bg("BG-WS18-BEFORE")
    expiry = datetime.fromisoformat(bg.expires_at)
    assert run(context(), c, decision="REFUSE", bg=bg, now=expiry - timedelta(microseconds=1)).status == "FORMED"


def test_ws18_003_break_glass_is_valid_at_exact_issue_boundary():
    c, bg = signed_bg("BG-WS18-ISSUED")
    issued = datetime.fromisoformat(bg.issued_at)
    assert run(context(), c, decision="REFUSE", bg=bg, now=issued).status == "FORMED"
