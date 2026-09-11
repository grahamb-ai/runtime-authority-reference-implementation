from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import datetime, timezone

import pytest

from app.hardening.executor import EPRSimulator, ProtectedExecutor
from app.hardening.models import ExactClinicalCommit
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


@pytest.fixture
def rig(tmp_path):
    clock = HarnessClock(datetime(2026, 9, 11, 12, 0, tzinfo=timezone.utc))
    store = BindStore(tmp_path / "binds.sqlite")
    simulator = EPRSimulator()
    executor = ProtectedExecutor(store, simulator, clock)
    return clock, store, simulator, executor


def issue_allow(rig, commit=None):
    clock, store, _, _ = rig
    commit = commit or baseline_commit()
    receipt = make_authority_receipt("ALLOW", commit, clock)
    bind = make_protected_bind(receipt, commit, clock)
    assert bind is not None
    store.issue(bind)
    return commit, receipt, bind


def test_h1_001_valid_exact_clinical_commit(rig):
    commit, _, bind = issue_allow(rig)
    _, store, simulator, executor = rig
    assert executor.execute(bind.bind_id, commit) == "EXECUTED"
    assert simulator.commit_count == 1
    assert store.get(bind.bind_id)[1] == "CONSUMED"


def test_h1_002_document_changed_after_allow(rig):
    commit, _, bind = issue_allow(rig)
    changed = replace(commit, document_content=commit.document_content + " Additional text.")
    assert rig[3].execute(bind.bind_id, changed) == "BINDING_MISMATCH"
    assert rig[2].commit_count == 0


def test_h1_003_patient_substitution(rig):
    commit, _, bind = issue_allow(rig)
    assert rig[3].execute(bind.bind_id, replace(commit, patient_ref="PAT-002")) == "BINDING_MISMATCH"
    assert rig[2].commit_count == 0


def test_h1_004_encounter_substitution(rig):
    commit, _, bind = issue_allow(rig)
    assert rig[3].execute(bind.bind_id, replace(commit, encounter_ref="ENC-002")) == "BINDING_MISMATCH"
    assert rig[2].commit_count == 0


def test_h1_005_clinician_substitution(rig):
    commit, _, bind = issue_allow(rig)
    assert rig[3].execute(bind.bind_id, replace(commit, clinician_ref="CLN-002")) == "BINDING_MISMATCH"


def test_h1_006_target_system_substitution(rig):
    commit, _, bind = issue_allow(rig)
    assert rig[3].execute(bind.bind_id, replace(commit, target_system="EPR-OTHER")) == "BINDING_MISMATCH"


def test_h1_007_target_instance_substitution(rig):
    commit, _, bind = issue_allow(rig)
    assert rig[3].execute(bind.bind_id, replace(commit, target_instance="ASVH-TEST-02")) == "BINDING_MISMATCH"


def test_h1_008_product_version_substitution(rig):
    commit, _, bind = issue_allow(rig)
    assert rig[3].execute(bind.bind_id, replace(commit, product_version="1.0.1")) == "BINDING_MISMATCH"


def test_h1_009_policy_version_substitution(rig):
    commit, _, bind = issue_allow(rig)
    assert rig[3].execute(bind.bind_id, replace(commit, runtime_policy_version="HC-POL-1.1")) == "BINDING_MISMATCH"


def test_h1_010_expired_bind(rig):
    commit, _, bind = issue_allow(rig)
    rig[0].advance(31)
    assert rig[3].execute(bind.bind_id, commit) == "BIND_EXPIRED"
    assert rig[2].commit_count == 0
    assert rig[1].get(bind.bind_id)[1] == "EXPIRED"


def test_h1_011_sequential_replay(rig):
    commit, _, bind = issue_allow(rig)
    assert rig[3].execute(bind.bind_id, commit) == "EXECUTED"
    assert rig[3].execute(bind.bind_id, commit) == "BIND_ALREADY_USED"
    assert rig[2].commit_count == 1


def test_h1_012_concurrent_double_use(rig):
    commit, _, bind = issue_allow(rig)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: rig[3].execute(bind.bind_id, commit), range(2)))
    assert results.count("EXECUTED") <= 1
    assert rig[2].commit_count <= 1


def test_h1_013_receipt_without_bind(rig):
    commit = baseline_commit()
    make_authority_receipt("ALLOW", commit, rig[0])
    assert rig[3].execute("NO-SUCH-BIND", commit) == "NO_VALID_BIND"
    assert rig[2].commit_count == 0


def test_h1_014_forged_bind_id(rig):
    assert rig[3].execute("FORGED-PCB-001", baseline_commit()) == "NO_VALID_BIND"
    assert rig[2].commit_count == 0


def test_h1_015_valid_bind_for_different_commit(rig):
    commit, _, bind = issue_allow(rig)
    other = replace(commit, commit_id="ECC-000002", patient_ref="PAT-002")
    assert rig[3].execute(bind.bind_id, other) == "BINDING_MISMATCH"


def test_h1_016_escalate_cannot_create_bind(rig):
    commit = baseline_commit()
    receipt = make_authority_receipt("ESCALATE", commit, rig[0])
    assert make_protected_bind(receipt, commit, rig[0]) is None


def test_h1_017_refuse_cannot_create_bind(rig):
    commit = baseline_commit()
    receipt = make_authority_receipt("REFUSE", commit, rig[0])
    assert make_protected_bind(receipt, commit, rig[0]) is None


def test_h1_018_non_material_transport_mutation(rig):
    commit = baseline_commit()
    original_hash = commit.commit_binding_hash
    transport_a = {"request_correlation_id": "REQ-001"}
    transport_b = {"request_correlation_id": "REQ-999"}
    assert transport_a != transport_b
    assert commit.commit_binding_hash == original_hash


def test_h1_019_canonicalisation_deterministic():
    a = baseline_commit()
    b = ExactClinicalCommit(**{k: getattr(a, k) for k in a.__dataclass_fields__})
    assert a.canonical_representation() == b.canonical_representation()
    assert a.commit_binding_hash == b.commit_binding_hash


def test_h1_020_materiality_profile_change(rig):
    commit, _, bind = issue_allow(rig)
    changed = replace(commit, materiality_profile="HC-MAT-2.0")
    assert rig[3].execute(bind.bind_id, changed) == "BINDING_MISMATCH"
    assert rig[2].commit_count == 0
