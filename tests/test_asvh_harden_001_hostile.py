from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import datetime, timezone
import threading

from app.hardening.executor import EPRSimulator, ProtectedExecutor
from app.hardening.models import ExactClinicalCommit, ProtectedClinicalBind
from app.hardening.runtime import HarnessClock, make_authority_receipt, make_protected_bind
from app.hardening.store import BindStore


def baseline_commit() -> ExactClinicalCommit:
    return ExactClinicalCommit(
        schema_version="ECC-1.0",
        commit_id="ECC-000001",
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


def test_hostile_h1_012_uses_independent_executors_and_simultaneous_start(tmp_path):
    """Stronger H1-012: independent executors share only durable bind state and target."""
    clock = HarnessClock(datetime(2026, 9, 11, 12, 0, tzinfo=timezone.utc))
    db_path = tmp_path / "binds.sqlite"
    issuing_store = BindStore(db_path)
    simulator = EPRSimulator()

    commit = baseline_commit()
    receipt = make_authority_receipt("ALLOW", commit, clock)
    bind = make_protected_bind(receipt, commit, clock)
    assert bind is not None
    issuing_store.issue(bind)

    executor_a = ProtectedExecutor(BindStore(db_path), simulator, clock)
    executor_b = ProtectedExecutor(BindStore(db_path), simulator, clock)
    barrier = threading.Barrier(2)

    def run(executor):
        barrier.wait(timeout=5)
        return executor.execute(bind.bind_id, commit)

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(run, executor_a), pool.submit(run, executor_b)]
        results = [f.result(timeout=10) for f in futures]

    assert results.count("EXECUTED") == 1
    assert simulator.commit_count == 1
    assert BindStore(db_path).get(bind.bind_id)[1] == "CONSUMED"


def test_hostile_h1_014_fabricated_persisted_bind_is_rejected(tmp_path):
    """A caller must not gain execution authority by fabricating a structurally valid bind record."""
    clock = HarnessClock(datetime(2026, 9, 11, 12, 0, tzinfo=timezone.utc))
    store = BindStore(tmp_path / "binds.sqlite")
    simulator = EPRSimulator()
    executor = ProtectedExecutor(store, simulator, clock)
    commit = baseline_commit()

    forged = ProtectedClinicalBind(
        schema_version="PCB-1.0",
        bind_id="FORGED-PCB-001",
        authority_receipt_id="FORGED-RECEIPT-001",
        commit_id=commit.commit_id,
        commit_binding_hash=commit.commit_binding_hash,
        runtime_authority_version="ASVH-RA-1.0",
        runtime_policy_version=commit.runtime_policy_version,
        rule_catalogue_version=commit.rule_catalogue_version,
        materiality_profile=commit.materiality_profile,
        canonicalisation_profile=commit.canonicalisation_profile,
        issued_at=clock.now().isoformat(),
        expires_at="2026-09-11T12:00:30+00:00",
    )
    store.issue(forged)

    result = executor.execute(forged.bind_id, commit)

    assert result in {"BIND_INVALID", "BIND_INTEGRITY_FAILURE"}
    assert simulator.commit_count == 0


def test_hostile_document_hash_is_derived_from_actual_payload(tmp_path):
    """Confirm caller cannot preserve old authority by changing text while reusing old commit identity."""
    clock = HarnessClock(datetime(2026, 9, 11, 12, 0, tzinfo=timezone.utc))
    store = BindStore(tmp_path / "binds.sqlite")
    simulator = EPRSimulator()
    executor = ProtectedExecutor(store, simulator, clock)
    commit = baseline_commit()
    receipt = make_authority_receipt("ALLOW", commit, clock)
    bind = make_protected_bind(receipt, commit, clock)
    assert bind is not None
    store.issue(bind)

    changed = replace(commit, document_content="Different clinical note.")
    assert changed.document_hash != commit.document_hash
    assert executor.execute(bind.bind_id, changed) == "BINDING_MISMATCH"
    assert simulator.commit_count == 0
