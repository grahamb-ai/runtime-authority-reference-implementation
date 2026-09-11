from dataclasses import replace

from app.hardening.runtime import compute_bind_integrity
from tests.test_asvh_whole_stack_hostile import context, run, valid_bind


def _resign(bind, **changes):
    altered = replace(bind, **changes, integrity_reference="")
    return replace(altered, integrity_reference=compute_bind_integrity(altered))


def test_ws32_001_unsupported_runtime_authority_version_cannot_form():
    c, b = valid_bind()
    hostile = _resign(b, runtime_authority_version="ASVH-RA-999")
    assert run(context(), c, hostile).status != "FORMED"


def test_ws32_002_valid_runtime_authority_version_control_forms():
    assert run(context()).status == "FORMED"
