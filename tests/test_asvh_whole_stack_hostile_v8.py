import shutil

from app.hardening.deployment_enforcement import DeploymentEnforcer
from app.hardening.store import BindStore
from app.hardening.whole_stack import WholeStackExecutionCoordinator
from tests.test_asvh_whole_stack_hostile import NOW, context, profile, valid_bind


def execute(store, commit, bind):
    coord = WholeStackExecutionCoordinator(DeploymentEnforcer(profile()), bind_store=store)
    return coord.execute(
        context=context(),
        supplied_profile=profile(),
        route_id="EPR-COMMIT",
        target_capability="EPR_WRITE",
        commit=commit,
        bind=bind,
        original_decision="ALLOW",
        control_contract_version="CC-1.0",
        now=NOW,
    )


def test_ws8_001_rollback_of_bind_database_cannot_resurrect_claimed_bind(tmp_path):
    c, b = valid_bind()
    db = tmp_path / "binds.sqlite"
    snapshot = tmp_path / "binds-before-claim.sqlite"
    store = BindStore(db)
    store.issue(b)
    shutil.copyfile(db, snapshot)

    assert execute(store, c, b).status == "FORMED"

    # Restore a coherent pre-claim copy of the operational claim database.
    shutil.copyfile(snapshot, db)
    restored = BindStore(db)
    assert execute(restored, c, b).status != "FORMED"


def test_ws8_002_replacing_bind_database_cannot_resurrect_claimed_bind(tmp_path):
    c, b = valid_bind()
    db = tmp_path / "binds.sqlite"
    store = BindStore(db)
    store.issue(b)
    assert execute(store, c, b).status == "FORMED"

    db.unlink()
    replacement = BindStore(db)
    replacement.issue(b)
    assert execute(replacement, c, b).status != "FORMED"


def test_ws8_003_claim_store_failure_is_indeterminate(tmp_path, monkeypatch):
    c, b = valid_bind()
    store = BindStore(tmp_path / "binds.sqlite")
    store.issue(b)

    def fail_claim(*args, **kwargs):
        raise RuntimeError("claim store unavailable")

    monkeypatch.setattr(store, "claim", fail_claim)
    result = execute(store, c, b)
    assert result.status == "INDETERMINATE"


def test_ws8_004_normal_durable_claim_still_forms_once(tmp_path):
    c, b = valid_bind()
    store = BindStore(tmp_path / "binds.sqlite")
    store.issue(b)
    assert execute(store, c, b).status == "FORMED"
