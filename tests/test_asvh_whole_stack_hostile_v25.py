from dataclasses import replace

from tests.test_asvh_whole_stack_hostile import run
from tests.test_asvh_whole_stack_hostile_v24 import _context_for
from tests.test_asvh_harden_001 import baseline_commit


def test_ws25_001_blank_document_type_cannot_form():
    c = replace(baseline_commit(), document_type="")
    assert run(_context_for(c), commit=c).status != "FORMED"


def test_ws25_002_blank_execution_type_cannot_form():
    c = replace(baseline_commit(), execution_type="   ")
    assert run(_context_for(c), commit=c).status != "FORMED"


def test_ws25_003_blank_workflow_context_cannot_form():
    c = replace(baseline_commit(), workflow_context="")
    assert run(_context_for(c), commit=c).status != "FORMED"


def test_ws25_004_blank_intended_use_cannot_form():
    c = replace(baseline_commit(), intended_use="   ")
    assert run(_context_for(c), commit=c).status != "FORMED"


def test_ws25_005_blank_materiality_profile_cannot_form():
    c = replace(baseline_commit(), materiality_profile="")
    assert run(_context_for(c), commit=c).status != "FORMED"


def test_ws25_006_blank_canonicalisation_profile_cannot_form():
    c = replace(baseline_commit(), canonicalisation_profile="   ")
    assert run(_context_for(c), commit=c).status != "FORMED"


def test_ws25_007_valid_control_still_forms():
    c = baseline_commit()
    assert run(_context_for(c), commit=c).status == "FORMED"
