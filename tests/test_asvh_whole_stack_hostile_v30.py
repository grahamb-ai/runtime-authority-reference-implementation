from dataclasses import replace

from app.hardening.runtime import compute_bind_integrity
from tests.test_asvh_whole_stack_hostile import context, run, valid_bind


def _resign(bind, **changes):
    altered = replace(bind, **changes, integrity_reference="")
    return replace(altered, integrity_reference=compute_bind_integrity(altered))


def test_ws30_001_blank_bind_id_cannot_form():
    c, b = valid_bind()
    assert run(context(), c, _resign(b, bind_id="")).status != "FORMED"


def test_ws30_002_blank_authority_receipt_id_cannot_form():
    c, b = valid_bind()
    assert run(context(), c, _resign(b, authority_receipt_id="   ")).status != "FORMED"


def test_ws30_003_blank_runtime_authority_version_cannot_form():
    c, b = valid_bind()
    assert run(context(), c, _resign(b, runtime_authority_version="")).status != "FORMED"


def test_ws30_004_bind_materiality_profile_must_match_exact_commit():
    c, b = valid_bind()
    assert run(context(), c, _resign(b, materiality_profile="HC-MAT-OTHER")).status != "FORMED"


def test_ws30_005_bind_canonicalisation_profile_must_match_exact_commit():
    c, b = valid_bind()
    assert run(context(), c, _resign(b, canonicalisation_profile="ECC-C14N-OTHER")).status != "FORMED"


def test_ws30_006_blank_bind_schema_version_cannot_form():
    c, b = valid_bind()
    assert run(context(), c, _resign(b, schema_version="")).status != "FORMED"


def test_ws30_007_valid_control_still_forms():
    assert run(context()).status == "FORMED"
