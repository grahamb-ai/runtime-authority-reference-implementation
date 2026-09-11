from dataclasses import replace

from tests.test_asvh_whole_stack_hostile import run
from tests.test_asvh_whole_stack_hostile_v24 import _context_for
from tests.test_asvh_harden_001 import baseline_commit


def test_ws26_001_blank_schema_version_cannot_form():
    c = replace(baseline_commit(), schema_version="")
    assert run(_context_for(c), commit=c).status != "FORMED"


def test_ws26_002_empty_document_content_cannot_form():
    c = replace(baseline_commit(), document_content="")
    assert run(_context_for(c), commit=c).status != "FORMED"


def test_ws26_003_whitespace_document_content_cannot_form():
    c = replace(baseline_commit(), document_content="   \n\t")
    assert run(_context_for(c), commit=c).status != "FORMED"


def test_ws26_004_valid_control_still_forms():
    c = baseline_commit()
    assert run(_context_for(c), commit=c).status == "FORMED"
