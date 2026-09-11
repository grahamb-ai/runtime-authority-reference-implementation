from dataclasses import replace
from datetime import datetime, timezone

import pytest

from app.hardening.continuity import (
    ContinuityProtectedExecutor,
    MutableStandingProvider,
    PresentStandingSnapshot,
    StateWatermarkStore,
)
from app.hardening.executor import EPRSimulator
from app.hardening.models import ExactClinicalCommit
from app.hardening.runtime import HarnessClock, make_authority_receipt, make_protected_bind
from app.hardening.store import BindStore


def baseline_commit(commit_id="ECC-H2-001") -> ExactClinicalCommit:
    return ExactClinicalCommit(
        schema_version="ECC-1.0",
        commit_id=commit_id,
        patient_ref="PAT-001",
        encounter_ref="ENC-001",
        consultation_ref="CON-001",
        clinician_ref="CLN-001",
        document_type="CLINICAL_NOTE",
        document_content="Baseline approved clinical note.",
        execution_type="EPR_COMMIT",
        target_system="EPR-SIMULATOR",
        target_instance="ASVH-TEST-01",
        target_record_ref="ENC-001",
        product_identifier="AVT-001",
        product_version="1.0.0",
        workflow_context="AMBIENT_SCRIBING",
        intended_use="CLINICAL_DOCUMENTATION",
        runtime_policy_version="HC-POL-1.0",
        rule_catalogue_version="ASVH-RC-1.0",
    )


def standing(sequence=1, **changes) -> PresentStandingSnapshot:
    base = PresentStandingSnapshot(
        source_id="HC-STATE-01",
        state_epoch=1,
        sequence=sequence,
        observed_at="2026-09-11T12:00:00+00:00",
        product_authorised=True,
        workflow_valid=True,
        monitoring_clear=True,
        policy_version="HC-POL-1.0",
        available=True,
    )
    return replace(base, **changes)


@pytest.fixture
def rig(tmp_path):
    clock = HarnessClock(datetime(2026, 9, 11, 12, 0, tzinfo=timezone.utc))
    bind_db = tmp_path / "binds.sqlite"
    watermark_db = tmp_path / "watermark.sqlite"
    store = BindStore(bind_db)
    simulator = EPRSimulator()
    provider = MutableStandingProvider(standing())
    watermarks = StateWatermarkStore(watermark_db)
    return clock, bind_db, watermark_db, store, simulator, provider, watermarks


def issue(rig, commit=None):
    clock, _, _, store, _, _, _ = rig
    commit = commit or baseline_commit()
    receipt = make_authority_receipt("ALLOW", commit, clock)
    bind = make_protected_bind(receipt, commit, clock)
    assert bind is not None
    store.issue(bind)
    return commit, bind


def executor(rig, hook=None):
    clock, _, _, store, simulator, provider, watermarks = rig
    return ContinuityProtectedExecutor(store, simulator, clock, provider, watermarks, hook)


def test_h2_001_valid_standing_at_execution(rig):
    commit, bind = issue(rig)
    assert executor(rig).execute(bind.bind_id, commit) == "EXECUTED"
    assert rig[4].commit_count == 1


def test_h2_002_product_authorisation_revoked_after_allow(rig):
    commit, bind = issue(rig)
    rig[5].set(standing(sequence=2, product_authorised=False))
    assert executor(rig).execute(bind.bind_id, commit) == "PRESENT_STANDING_INVALID"
    assert rig[4].commit_count == 0


def test_h2_003_monitoring_breach_after_allow(rig):
    commit, bind = issue(rig)
    rig[5].set(standing(sequence=2, monitoring_clear=False))
    assert executor(rig).execute(bind.bind_id, commit) == "PRESENT_STANDING_INVALID"
    assert rig[4].commit_count == 0


def test_h2_004_current_standing_unavailable(rig):
    commit, bind = issue(rig)
    rig[5].set(standing(sequence=2, available=False))
    assert executor(rig).execute(bind.bind_id, commit) == "PRESENT_STANDING_UNAVAILABLE"
    assert rig[4].commit_count == 0


def test_h2_005_policy_version_changes_after_allow(rig):
    commit, bind = issue(rig)
    rig[5].set(standing(sequence=2, policy_version="HC-POL-2.0"))
    assert executor(rig).execute(bind.bind_id, commit) == "PRESENT_STANDING_INVALID"
    assert rig[4].commit_count == 0


def test_h2_006_state_changes_during_protected_interval(rig):
    commit, bind = issue(rig)

    def revoke():
        rig[5].set(standing(sequence=2, product_authorised=False))

    assert executor(rig, revoke).execute(bind.bind_id, commit) == "PRESENT_STANDING_CHANGED"
    assert rig[4].commit_count == 0


def test_h2_007_bind_expires_during_protected_interval(rig):
    commit, bind = issue(rig)

    def expire():
        rig[0].advance(31)

    assert executor(rig, expire).execute(bind.bind_id, commit) == "BIND_EXPIRED"
    assert rig[4].commit_count == 0


def test_h2_008_stale_state_replay_after_high_watermark(rig):
    commit1, bind1 = issue(rig, baseline_commit("ECC-H2-008-A"))
    rig[5].set(standing(sequence=5))
    assert executor(rig).execute(bind1.bind_id, commit1) == "EXECUTED"

    commit2, bind2 = issue(rig, baseline_commit("ECC-H2-008-B"))
    rig[5].set(standing(sequence=4))
    assert executor(rig).execute(bind2.bind_id, commit2) == "STATE_ROLLBACK_DETECTED"
    assert rig[4].commit_count == 1


def test_h2_009_high_watermark_survives_executor_restart(rig):
    commit1, bind1 = issue(rig, baseline_commit("ECC-H2-009-A"))
    rig[5].set(standing(sequence=7))
    assert executor(rig).execute(bind1.bind_id, commit1) == "EXECUTED"

    new_store = BindStore(rig[1])
    new_watermarks = StateWatermarkStore(rig[2])
    new_provider = MutableStandingProvider(standing(sequence=6))
    new_executor = ContinuityProtectedExecutor(new_store, rig[4], rig[0], new_provider, new_watermarks)

    commit2 = baseline_commit("ECC-H2-009-B")
    receipt2 = make_authority_receipt("ALLOW", commit2, rig[0])
    bind2 = make_protected_bind(receipt2, commit2, rig[0])
    assert bind2 is not None
    new_store.issue(bind2)

    assert new_executor.execute(bind2.bind_id, commit2) == "STATE_ROLLBACK_DETECTED"
    assert rig[4].commit_count == 1


def test_h2_010_caller_time_cannot_extend_expired_bind(rig):
    commit, bind = issue(rig)
    caller_supplied_future_time = "2099-01-01T00:00:00+00:00"
    assert caller_supplied_future_time > bind.expires_at
    rig[0].advance(31)
    assert executor(rig).execute(bind.bind_id, commit) == "BIND_EXPIRED"
    assert rig[4].commit_count == 0


def test_h2_011_forward_valid_state_change_is_permitted(rig):
    commit, bind = issue(rig)

    def advance_valid_state():
        rig[5].set(standing(sequence=2))

    assert executor(rig, advance_valid_state).execute(bind.bind_id, commit) == "EXECUTED"
    assert rig[4].commit_count == 1


def test_h2_012_exact_commit_binding_still_enforced(rig):
    commit, bind = issue(rig)
    changed = replace(commit, document_content="Different clinical note.")
    assert executor(rig).execute(bind.bind_id, changed) == "BINDING_MISMATCH"
    assert rig[4].commit_count == 0
