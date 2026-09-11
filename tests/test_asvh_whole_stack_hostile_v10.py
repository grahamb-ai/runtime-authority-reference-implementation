from concurrent.futures import ThreadPoolExecutor

from app.hardening.deployment_enforcement import (
    BreakGlassAuthority,
    DeploymentEnforcer,
    sign_break_glass_authority,
)
from app.hardening.store import BreakGlassUseStore
from app.hardening.whole_stack import WholeStackExecutionCoordinator
from tests.test_asvh_whole_stack_hostile import NOW, context, profile, valid_bind


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


def execute(store_path, c, bg):
    p = profile()
    enforcer = DeploymentEnforcer(p, break_glass_store=BreakGlassUseStore(store_path))
    coord = WholeStackExecutionCoordinator(enforcer)
    return coord.execute(
        context=context(),
        supplied_profile=p,
        route_id="EPR-COMMIT",
        target_capability="EPR_WRITE",
        commit=c,
        bind=None,
        original_decision="REFUSE",
        control_contract_version="CC-1.0",
        now=NOW,
        break_glass=bg,
    )


def test_ws10_001_same_break_glass_replay_after_enforcer_restart_cannot_form_twice(tmp_path):
    c, bg = signed_bg()
    store_path = tmp_path / "break-glass.sqlite"
    first = execute(store_path, c, bg)
    second = execute(store_path, c, bg)
    assert first.status == "FORMED"
    assert second.status != "FORMED"


def test_ws10_002_same_break_glass_across_two_enforcers_at_most_one_forms(tmp_path):
    c, bg = signed_bg()
    store_path = tmp_path / "break-glass.sqlite"
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: execute(store_path, c, bg), range(2)))
    assert sum(r.status == "FORMED" for r in results) <= 1


def test_ws10_003_distinct_integrity_bound_break_glass_authorities_can_each_form(tmp_path):
    c1, bg1 = signed_bg("BG-WS10-A")
    c2, bg2 = signed_bg("BG-WS10-B")
    store_path = tmp_path / "break-glass.sqlite"
    assert bg1.override_id != bg2.override_id
    r1 = execute(store_path, c1, bg1)
    r2 = execute(store_path, c2, bg2)
    assert r1.status == "FORMED"
    assert r2.status == "FORMED"
