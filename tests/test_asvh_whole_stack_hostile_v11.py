import shutil

from app.hardening.deployment_enforcement import DeploymentEnforcer
from app.hardening.store import BreakGlassUseStore
from app.hardening.whole_stack import WholeStackExecutionCoordinator
from tests.test_asvh_whole_stack_hostile import NOW, context, profile
from tests.test_asvh_whole_stack_hostile_v10 import signed_bg


def _execute_with_store(c, bg, store):
    p = profile()
    coord = WholeStackExecutionCoordinator(DeploymentEnforcer(p, break_glass_store=store))
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


def test_ws11_001_rollback_of_break_glass_replay_db_cannot_resurrect_consumed_override(tmp_path):
    c, bg = signed_bg("BG-WS11-ROLLBACK")
    db = tmp_path / "break-glass.sqlite"
    snapshot = tmp_path / "break-glass-before-use.sqlite"
    store = BreakGlassUseStore(db)
    shutil.copyfile(db, snapshot)

    assert _execute_with_store(c, bg, store).status == "FORMED"

    # Restore a coherent pre-consumption copy of the replay database.
    shutil.copyfile(snapshot, db)
    restored = BreakGlassUseStore(db)
    assert _execute_with_store(c, bg, restored).status != "FORMED"


def test_ws11_002_replacing_break_glass_replay_db_cannot_resurrect_consumed_override(tmp_path):
    c, bg = signed_bg("BG-WS11-REPLACE")
    db = tmp_path / "break-glass.sqlite"
    store = BreakGlassUseStore(db)
    assert _execute_with_store(c, bg, store).status == "FORMED"

    db.unlink()
    replacement = BreakGlassUseStore(db)
    assert _execute_with_store(c, bg, replacement).status != "FORMED"


def test_ws11_003_untouched_durable_replay_state_rejects_second_use(tmp_path):
    c, bg = signed_bg("BG-WS11-CONTROL")
    store = BreakGlassUseStore(tmp_path / "break-glass.sqlite")
    assert _execute_with_store(c, bg, store).status == "FORMED"
    assert _execute_with_store(c, bg, store).status != "FORMED"
