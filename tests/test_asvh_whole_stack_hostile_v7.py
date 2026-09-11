from concurrent.futures import ThreadPoolExecutor

from app.hardening.deployment_enforcement import DeploymentEnforcer
from app.hardening.whole_stack import WholeStackExecutionCoordinator
from tests.test_asvh_whole_stack_hostile import NOW, context, profile, valid_bind


def execute(coord, ctx, commit, bind):
    p = profile()
    return coord.execute(
        context=ctx,
        supplied_profile=p,
        route_id="EPR-COMMIT",
        target_capability="EPR_WRITE",
        commit=commit,
        bind=bind,
        original_decision="ALLOW",
        control_contract_version="CC-1.0",
        now=NOW,
    )


def new_coordinator():
    return WholeStackExecutionCoordinator(DeploymentEnforcer(profile()))


def test_ws7_001_same_bind_replay_after_coordinator_restart_cannot_form_twice():
    c, b = valid_bind()
    first = execute(new_coordinator(), context(), c, b)
    second = execute(new_coordinator(), context(), c, b)
    assert first.status == "FORMED"
    assert second.status != "FORMED"


def test_ws7_002_same_bind_across_two_coordinators_at_most_one_forms():
    c, b = valid_bind()
    coords = (new_coordinator(), new_coordinator())
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda coord: execute(coord, context(), c, b), coords))
    assert sum(r.status == "FORMED" for r in results) <= 1


def test_ws7_003_two_distinct_valid_binds_can_each_form():
    c1, b1 = valid_bind()
    c2, b2 = valid_bind()
    assert b1.bind_id != b2.bind_id
    r1 = execute(new_coordinator(), context(), c1, b1)
    r2 = execute(new_coordinator(), context(), c2, b2)
    assert r1.status == "FORMED"
    assert r2.status == "FORMED"
