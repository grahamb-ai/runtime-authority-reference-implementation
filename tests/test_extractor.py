## @file test_extractor.py
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Basic extractor tests against the shared sample policy fixture.
#
"""Unit tests for rule extraction.

Pure tests: no database, no HTTP. They parse the bundled sample policy fixture
and assert the extractor produces exactly the rules we expect.
"""

from pathlib import Path

from app.engines.extractor import extract_rules
from app.engines.parser import extract_text

FIXTURE = Path(__file__).parent / "fixtures" / "sample-policy.txt"

## @fn _rules()
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test helper that runs the extractor against the shared sample policy fixture.
#
def _rules():
    """Helper: parse the fixture and return the extracted rules."""
    text = extract_text(FIXTURE)
    return extract_rules(text, source_document="sample-policy.txt")


## @fn test_extracts_three_authorized_roles()
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test: Extracts three authorized roles.
#
def test_extracts_three_authorized_roles():
    # "Authorized roles for payment.release: regional_manager, finance_director, cfo."
    rules = _rules()
    roles = [r.value for r in rules if r.attribute == "authorized_role"]
    assert sorted(roles) == ["cfo", "finance_director", "regional_manager"]

## @fn test_extracts_per_role_ceilings()
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test: Extracts per role ceilings.
#
def test_extracts_per_role_ceilings():
    # Two "The <role> may approve ... up to <amount>" sentences.
    rules = _rules()
    limits = {r.subject: r.value for r in rules if r.attribute == "max_amount"}
    assert limits["regional_manager"] == 100000
    assert limits["finance_director"] == 500000

## @fn test_extracts_conditional_evidence_rule()
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test: Extracts conditional evidence rule.
#
def test_extracts_conditional_evidence_rule():
    # "Any payment.release above 50,000 EUR must be accompanied by invoice and purchase_order."
    rules = _rules()
    evidence = [r for r in rules if r.attribute == "required_evidence"]
    assert len(evidence) == 1
    rule = evidence[0]
    assert rule.threshold == 50000
    assert sorted(rule.value) == ["invoice", "purchase_order"]

## @fn test_rules_are_tagged_by_type()
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test: Rules are tagged by type.
#
def test_rules_are_tagged_by_type():
    # 3 authorized_role + 2 max_amount = 5 authority; 1 admissibility.
    rules = _rules()
    authority = [r for r in rules if r.rule_type == "authority"]
    admissibility = [r for r in rules if r.rule_type == "admissibility"]
    assert len(authority) == 5
    assert len(admissibility) == 1

## @fn test_source_excerpt_is_captured()
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test: Source excerpt is captured.
#
def test_source_excerpt_is_captured():
    # Every rule must carry its audit trail (excerpt + source document).
    rules = _rules()
    assert all(r.source_excerpt for r in rules)
    assert all(r.source_document == "sample-policy.txt" for r in rules)
