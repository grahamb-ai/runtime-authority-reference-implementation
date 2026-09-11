from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace

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


def test_ws6_001_forged_bind_integrity_cannot_form():
    c, b = valid_bind()
    forged = replace(b, integrity_reference="PCB-HMAC-SHA256-1:deadbeef")
    coord = WholeStackExecutionCoordinator(DeploymentEnforcer(profile()))
    assert execute(coord, context(), c, forged).status != "FORMED"


def test_ws6_002_non_single_use_bind_cannot_form():
    c, b = valid_bind()
    forged = replace(b, use_semantics="MULTI_USE")
    coord = WholeStackExecutionCoordinator(DeploymentEnforcer(profile()))
    assert execute(coord, context(), c, forged).status != "FORMED"


def test_ws6_003_sequential_same_bind_replay_cannot_form_twice():
    c, b = valid_bind()
    coord = WholeStackExecutionCoordinator(DeploymentEnforcer(profile()))
    first = execute(coord, context(), c, b)
    second = execute(coord, context(), c, b)
    assert first.status == "FORMED"
    assert second.status != "FORMED"


def test_ws6_004_concurrent_same_bind_at_most_one_forms():
    c, b = valid_bind()
    coord = WholeStackExecutionCoordinator(DeploymentEnforcer(profile()))
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: execute(coord, context(), c, b), range(2)))
    assert sum(r.status == "FORMED" for r in results) <= 1


def test_ws6_005_valid_unused_single_use_bind_can_form():
    c, b = valid_bind()
    coord = WholeStackExecutionCoordinator(DeploymentEnforcer(profile()))
    assert execute(coord, context(), c, b).status == "FORMED"
