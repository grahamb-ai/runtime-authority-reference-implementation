from datetime import datetime, timezone

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


def commit(commit_id):
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


def snapshot(source_id="HC-STATE-01", sequence=1, observed_at="2026-09-11T12:00:00+00:00", authorised=True):
    return PresentStandingSnapshot(
        source_id=source_id,
        state_epoch=1,
        sequence=sequence,
        observed_at=observed_at,
        product_authorised=authorised,
        workflow_valid=True,
        monitoring_clear=True,
        policy_version="HC-POL-1.0",
        available=True,
    )


def issue(store, clock, exact_commit):
    receipt = make_authority_receipt("ALLOW", exact_commit, clock)
    bind = make_protected_bind(receipt, exact_commit, clock)
    assert bind is not None
    store.issue(bind)
    return bind


def test_hostile_same_version_state_equivocation_does_not_restore_authority(tmp_path):
    clock = HarnessClock(datetime(2026, 9, 11, 12, 0, tzinfo=timezone.utc))
    store = BindStore(tmp_path / "binds.sqlite")
    watermarks = StateWatermarkStore(tmp_path / "watermarks.sqlite")
    simulator = EPRSimulator()
    provider = MutableStandingProvider(snapshot(sequence=5, authorised=False))
    ex = ContinuityProtectedExecutor(store, simulator, clock, provider, watermarks)

    c1 = commit("H2-HOSTILE-EQUIV-A")
    b1 = issue(store, clock, c1)
    assert ex.execute(b1.bind_id, c1) == "PRESENT_STANDING_INVALID"

    provider.set(snapshot(sequence=5, authorised=True))
    c2 = commit("H2-HOSTILE-EQUIV-B")
    b2 = issue(store, clock, c2)
    result = ex.execute(b2.bind_id, c2)

    assert result in {"STATE_EQUIVOCATION_DETECTED", "STATE_ROLLBACK_DETECTED"}
    assert simulator.commit_count == 0


def test_hostile_source_id_substitution_cannot_reset_high_watermark(tmp_path):
    clock = HarnessClock(datetime(2026, 9, 11, 12, 0, tzinfo=timezone.utc))
    store = BindStore(tmp_path / "binds.sqlite")
    watermarks = StateWatermarkStore(tmp_path / "watermarks.sqlite")
    simulator = EPRSimulator()
    provider = MutableStandingProvider(snapshot(source_id="HC-STATE-01", sequence=9))
    ex = ContinuityProtectedExecutor(store, simulator, clock, provider, watermarks)

    c1 = commit("H2-HOSTILE-SOURCE-A")
    b1 = issue(store, clock, c1)
    assert ex.execute(b1.bind_id, c1) == "EXECUTED"

    provider.set(snapshot(source_id="HC-STATE-FAKE", sequence=1))
    c2 = commit("H2-HOSTILE-SOURCE-B")
    b2 = issue(store, clock, c2)
    result = ex.execute(b2.bind_id, c2)

    assert result == "STATE_SOURCE_MISMATCH"
    assert simulator.commit_count == 1


def test_hostile_stale_high_sequence_snapshot_is_not_current_standing(tmp_path):
    clock = HarnessClock(datetime(2026, 9, 11, 12, 0, tzinfo=timezone.utc))
    store = BindStore(tmp_path / "binds.sqlite")
    watermarks = StateWatermarkStore(tmp_path / "watermarks.sqlite")
    simulator = EPRSimulator()
    provider = MutableStandingProvider(
        snapshot(sequence=999, observed_at="2026-09-11T10:00:00+00:00")
    )
    ex = ContinuityProtectedExecutor(store, simulator, clock, provider, watermarks)

    c = commit("H2-HOSTILE-STALE")
    b = issue(store, clock, c)
    result = ex.execute(b.bind_id, c)

    assert result == "PRESENT_STANDING_STALE"
    assert simulator.commit_count == 0
