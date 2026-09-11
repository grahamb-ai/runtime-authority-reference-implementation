from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace

from app.hardening.deployment_enforcement import (
    BreakGlassAuthority,
    sign_break_glass_authority,
)
from tests.test_asvh_whole_stack_hostile import context, run, valid_bind


def signed_bg(override_id="BG-WS10-1"):
    c, _ = valid_bind()
    authority = BreakGlassAuthority(
        override_id=override_id,
        authority_identity="CLINICAL-DUTY-MANAGER",
        commit_binding_hash=c.commit_binding_hash,
        deployment_id="DEP-01",
        issued_at="2026-09-11T11:55:00+00:00",
        expires_at="2026-09-11T12:05:00+00:00",
        policy_version="BG-1.0",
        single_use=True,
    )
    return c, sign_break_glass_authority(authority)


def execute(c, bg):
    return run(context(), c, decision="REFUSE", bg=bg)


def test_ws10_001_same_break_glass_replay_after_enforcer_restart_cannot_form_twice():
    c, bg = signed_bg()
    first = execute(c, bg)
    second = execute(c, bg)
    assert first.status == "FORMED"
    assert second.status != "FORMED"


def test_ws10_002_same_break_glass_across_two_enforcers_at_most_one_forms():
    c, bg = signed_bg()
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: execute(c, bg), range(2)))
    assert sum(r.status == "FORMED" for r in results) <= 1


def test_ws10_003_distinct_integrity_bound_break_glass_authorities_can_each_form():
    c1, bg1 = signed_bg("BG-WS10-A")
    c2, bg2 = signed_bg("BG-WS10-B")
    # Same exact consequence, but two independently issued override identities.
    assert bg1.override_id != bg2.override_id
    r1 = execute(c1, bg1)
    r2 = execute(c2, bg2)
    assert r1.status == "FORMED"
    assert r2.status == "FORMED"
