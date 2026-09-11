from dataclasses import replace

from tests.test_asvh_whole_stack_hostile import context, run, _layer_evidence
from tests.test_asvh_harden_001 import baseline_commit


def _context_for(c):
    base = context()
    return replace(
        base,
        evidence_subject_ref=c.patient_ref,
        evidence_product_identifier=c.product_identifier,
        evidence_product_version=c.product_version,
        authority_commit_binding_hash=c.commit_binding_hash,
        layer_evidence=_layer_evidence(c, "ACTIVE", "ACTIVE", "ALLOW", "ALLOW", "ALLOW"),
    )


def test_ws24_001_blank_patient_identity_cannot_form():
    c = replace(baseline_commit(), patient_ref="")
    assert run(_context_for(c), commit=c).status != "FORMED"


def test_ws24_002_blank_target_record_identity_cannot_form():
    c = replace(baseline_commit(), target_record_ref="   ")
    assert run(_context_for(c), commit=c).status != "FORMED"


def test_ws24_003_blank_commit_identifier_cannot_form():
    c = replace(baseline_commit(), commit_id="")
    assert run(_context_for(c), commit=c).status != "FORMED"


def test_ws24_004_blank_product_identifier_cannot_form():
    c = replace(baseline_commit(), product_identifier="")
    assert run(_context_for(c), commit=c).status != "FORMED"


def test_ws24_005_valid_control_still_forms():
    c = baseline_commit()
    assert run(_context_for(c), commit=c).status == "FORMED"
