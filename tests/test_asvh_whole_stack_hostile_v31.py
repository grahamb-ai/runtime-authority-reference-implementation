from dataclasses import replace

from app.hardening.runtime import compute_bind_integrity
from tests.test_asvh_harden_001 import baseline_commit
from tests.test_asvh_whole_stack_hostile import _layer_evidence, context, run, valid_bind


def _context_for(c):
    return replace(
        context(),
        authority_policy_version=c.runtime_policy_version,
        authority_rule_catalogue_version=c.rule_catalogue_version,
        evidence_subject_ref=c.patient_ref,
        evidence_product_identifier=c.product_identifier,
        evidence_product_version=c.product_version,
        authority_commit_binding_hash=c.commit_binding_hash,
        layer_evidence=_layer_evidence(c, "ACTIVE", "ACTIVE", "ALLOW", "ALLOW", "ALLOW"),
    )


def _resign(bind, **changes):
    altered = replace(bind, **changes, integrity_reference="")
    return replace(altered, integrity_reference=compute_bind_integrity(altered))


def test_ws31_001_unsupported_exact_commit_schema_cannot_form():
    c = replace(baseline_commit(), schema_version="ECC-999")
    assert run(_context_for(c), c).status != "FORMED"


def test_ws31_002_unsupported_materiality_profile_cannot_form():
    c = replace(baseline_commit(), materiality_profile="HC-MAT-OTHER")
    assert run(_context_for(c), c).status != "FORMED"


def test_ws31_003_unsupported_canonicalisation_profile_cannot_form():
    c = replace(baseline_commit(), canonicalisation_profile="ECC-C14N-OTHER")
    assert run(_context_for(c), c).status != "FORMED"


def test_ws31_004_unsupported_protected_bind_schema_cannot_form():
    c, b = valid_bind()
    assert run(context(), c, _resign(b, schema_version="PCB-999")).status != "FORMED"


def test_ws31_005_supported_profiles_control_forms():
    assert run(context()).status == "FORMED"
