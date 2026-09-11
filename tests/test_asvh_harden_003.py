from datetime import datetime, timezone

from app.hardening.consequence import ConsequenceAwareExecutor, ConsequenceReconciler, ReconcilableEPRSimulator, consequence_key
from app.hardening.models import ExactClinicalCommit
from app.hardening.runtime import HarnessClock, make_authority_receipt, make_protected_bind


def commit(commit_id="H3-ECC-001"):
    return ExactClinicalCommit(
        schema_version="ECC-1.0", commit_id=commit_id,
        patient_ref="PAT-001", encounter_ref="ENC-001", consultation_ref="CON-001", clinician_ref="CLN-001",
        document_type="CLINICAL_NOTE", document_content="Approved note.", execution_type="EPR_COMMIT",
        target_system="EPR-SIMULATOR", target_instance="ASVH-H3-01", target_record_ref="ENC-001",
        product_identifier="AVT-001", product_version="1.0.0", workflow_context="AMBIENT_SCRIBING",
        intended_use="CLINICAL_DOCUMENTATION", runtime_policy_version="HC-POL-1.0", rule_catalogue_version="ASVH-RC-1.0",
    )


def issued(c):
    clock = HarnessClock(datetime(2026, 9, 11, 12, 0, tzinfo=timezone.utc))
    receipt = make_authority_receipt("ALLOW", c, clock)
    bind = make_protected_bind(receipt, c, clock)
    assert bind is not None
    return receipt, bind


def rig():
    target = ReconcilableEPRSimulator()
    reconciler = ConsequenceReconciler(target)
    return target, reconciler, ConsequenceAwareExecutor(target, reconciler)


def test_h3_001_successful_ack_forms_consequence():
    c = commit(); receipt, bind = issued(c); target, _, ex = rig()
    ev = ex.execute(bind, receipt, c)
    assert ev.consequence_status == "FORMED"
    assert ev.provenance_level == "CE-2-TARGET-ACK"
    assert target.record_count() == 1


def test_h3_002_lost_ack_reconciles_to_formed():
    c = commit(); receipt, bind = issued(c); target, _, ex = rig()
    ev = ex.execute(bind, receipt, c, lose_ack=True)
    assert ev.consequence_status == "FORMED"
    assert ev.provenance_level == "CE-3-TARGET-READBACK"
    assert target.record_count() == 1


def test_h3_003_timeout_without_reconciliation_is_indeterminate():
    c = commit(); receipt, bind = issued(c); target, _, ex = rig()
    ev = ex.execute(bind, receipt, c, lose_ack=True, auto_reconcile=False)
    assert ev.consequence_status == "INDETERMINATE"
    assert target.record_count() == 1


def test_h3_004_failure_before_write_reconciles_to_prevented():
    c = commit(); receipt, bind = issued(c); target, _, ex = rig()
    ev = ex.execute(bind, receipt, c, fail_before_write=True)
    assert ev.consequence_status == "PREVENTED"
    assert target.record_count() == 0


def test_h3_005_retry_uses_stable_consequence_key():
    c = commit(); receipt, bind = issued(c); target, _, ex = rig()
    ev1 = ex.execute(bind, receipt, c, lose_ack=True, auto_reconcile=False)
    ev2 = ex.execute(bind, receipt, c)
    assert ev1.consequence_key == ev2.consequence_key == consequence_key(c)
    assert target.record_count() == 1


def test_h3_006_duplicate_retry_does_not_duplicate_consequence():
    c = commit(); receipt, bind = issued(c); target, _, ex = rig()
    ex.execute(bind, receipt, c)
    ex.execute(bind, receipt, c)
    assert target.record_count() == 1
    assert target.attempt_count(consequence_key(c)) == 2


def test_h3_007_evidence_binds_receipt_bind_and_commit():
    c = commit(); receipt, bind = issued(c); _, _, ex = rig()
    ev = ex.execute(bind, receipt, c)
    assert ev.bind_id == bind.bind_id
    assert ev.authority_receipt_id == receipt.receipt_id
    assert ev.commit_id == c.commit_id
    assert ev.commit_binding_hash == c.commit_binding_hash
    assert ev.target_record_ref == c.target_record_ref


def test_h3_008_target_readback_conflict_is_indeterminate():
    c = commit(); receipt, bind = issued(c); target, reconciler, _ = rig()
    key = consequence_key(c)
    target.commit(key, c)
    target._records[key]["commit_binding_hash"] = "sha256:conflict"
    ev = reconciler.reconcile(bind, receipt, c)
    assert ev.consequence_status == "INDETERMINATE"


def test_h3_009_absence_readback_is_prevented_inside_simulator_boundary():
    c = commit(); receipt, bind = issued(c); _, reconciler, _ = rig()
    ev = reconciler.reconcile(bind, receipt, c)
    assert ev.consequence_status == "PREVENTED"


def test_h3_010_receipt_alone_does_not_create_consequence_evidence():
    c = commit(); receipt, bind = issued(c); target, _, _ = rig()
    assert receipt.decision == "ALLOW"
    assert bind is not None
    assert target.record_count() == 0


def test_h3_011_different_exact_commit_has_different_consequence_key():
    c1 = commit("H3-ECC-A")
    c2 = commit("H3-ECC-B")
    assert consequence_key(c1) != consequence_key(c2)


def test_h3_012_target_reference_present_for_formed_evidence():
    c = commit(); receipt, bind = issued(c); _, _, ex = rig()
    ev = ex.execute(bind, receipt, c)
    assert ev.consequence_status == "FORMED"
    assert ev.target_reference is not None
