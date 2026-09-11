from dataclasses import replace
from datetime import datetime, timezone

from app.hardening.consequence import ConsequenceAwareExecutor, ConsequenceReconciler, ReconcilableEPRSimulator
from app.hardening.models import ExactClinicalCommit
from app.hardening.runtime import HarnessClock, make_authority_receipt, make_protected_bind


def commit(commit_id="H3-HOSTILE-ECC"):
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


def test_hostile_unrelated_receipt_cannot_be_attached_to_consequence():
    c = commit(); receipt, bind = issued(c)
    other = replace(receipt, receipt_id="UNRELATED-RECEIPT")
    target = ReconcilableEPRSimulator(); ex = ConsequenceAwareExecutor(target, ConsequenceReconciler(target))
    ev = ex.execute(bind, other, c)
    assert ev.consequence_status == "PREVENTED"
    assert "AUTHORITY_CHAIN_INVALID" in ev.detail
    assert target.record_count() == 0


def test_hostile_bind_for_different_commit_cannot_form_consequence():
    c1 = commit("H3-A"); receipt, bind = issued(c1)
    c2 = replace(c1, commit_id="H3-B", document_content="Different approved note")
    target = ReconcilableEPRSimulator(); ex = ConsequenceAwareExecutor(target, ConsequenceReconciler(target))
    ev = ex.execute(bind, receipt, c2)
    assert ev.consequence_status == "PREVENTED"
    assert "AUTHORITY_CHAIN_INVALID" in ev.detail
    assert target.record_count() == 0


def test_hostile_reconciliation_target_unavailable_remains_indeterminate():
    c = commit(); receipt, bind = issued(c)
    target = ReconcilableEPRSimulator(); reconciler = ConsequenceReconciler(target)
    def unavailable(_key):
        raise TimeoutError("target read-back unavailable")
    target.read_by_key = unavailable
    ev = reconciler.reconcile(bind, receipt, c)
    assert ev.consequence_status == "INDETERMINATE"
    assert "unavailable" in ev.detail.lower()
