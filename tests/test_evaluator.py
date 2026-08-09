## @file test_evaluator.py
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Core decision-engine tests: the four original acceptance scenarios A-D.
#
"""Acceptance tests for the decision engine.

Pure tests (no database, no HTTP). These encode the four canonical scenarios
A-D from the build spec -> the executable definition of "correct" for the engine.
"""

from pathlib import Path

import pytest

from app.engines.evaluator import evaluate
from app.engines.extractor import extract_rules
from app.engines.parser import extract_text
from app.engines.types import OrderData

FIXTURE = Path(__file__).parent / "fixtures" / "sample-policy.txt"


@pytest.fixture
## @fn rules()
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Pytest fixture providing a fixed set of extracted rules for the tests in this file.
#
def rules():
    """Extract the sample policy once and give each rule a stable id.

    The database normally assigns ids; in a pure test we inject them so the
    checks' ``rule_id`` audit references are populated.
    """
    text = extract_text(FIXTURE)
    extracted = extract_rules(text, source_document="sample-policy.txt")
    for i, r in enumerate(extracted):
        r.id = f"rule-{i}"
    return extracted

## @fn _order(role, amount, evidence)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test helper that builds an OrderData with sensible defaults for the scenario under test.
#  @param role See test body for how this fixture/argument is used.
#  @param amount See test body for how this fixture/argument is used.
#  @param evidence See test body for how this fixture/argument is used.
#
def _order(role, amount, evidence):
    """Build a payment.release order with the given role/amount/evidence."""
    return OrderData(
        action="payment.release",
        requester_role=role,
        target="SAP_PAYMENT_RELEASE",
        amount=amount,
        currency="EUR",
        evidence=evidence,
    )

## @fn test_scenario_a_allow(rules)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test: Scenario a allow.
#  @param rules See test body for how this fixture/argument is used.
#
def test_scenario_a_allow(rules):
    # Within ceiling and below the 50k evidence threshold -> ALLOW.
    record = evaluate(_order("regional_manager", 40000, ["invoice"]), rules)
    assert record.decision == "ALLOW"
    assert record.authority_state == "VALID"
    assert record.required_action is None

## @fn test_scenario_b_escalate_missing_evidence(rules)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test: Scenario b escalate missing evidence.
#  @param rules See test body for how this fixture/argument is used.
#
def test_scenario_b_escalate_missing_evidence(rules):
    # Authority ok; above 50k but purchase_order missing -> ESCALATE.
    record = evaluate(_order("regional_manager", 80000, ["invoice"]), rules)
    assert record.decision == "ESCALATE"
    assert "purchase_order" in (record.required_action or "")

## @fn test_scenario_c_escalate_over_limit(rules)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test: Scenario c escalate over limit.
#  @param rules See test body for how this fixture/argument is used.
#
def test_scenario_c_escalate_over_limit(rules):
    # Authority ok; amount exceeds the 100k ceiling -> ESCALATE.
    record = evaluate(
        _order("regional_manager", 250000, ["invoice", "purchase_order"]), rules
    )
    assert record.decision == "ESCALATE"
    assert record.authority_state == "VALID"
    assert any(c.name == "amount_within_limit" and not c.passed for c in record.checks)

## @fn test_scenario_d_refuse_unauthorized_role(rules)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test: Scenario d refuse unauthorized role.
#  @param rules See test body for how this fixture/argument is used.
#
def test_scenario_d_refuse_unauthorized_role(rules):
    # Role not authorized -> REFUSE, and admissibility must NOT be evaluated.
    record = evaluate(_order("intern", 10000, []), rules)
    assert record.decision == "REFUSE"
    assert record.required_action is None
    assert all(c.category == "authority" for c in record.checks)

## @fn test_unknown_action_is_refused(rules)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test: Unknown action is refused.
#  @param rules See test body for how this fixture/argument is used.
#
def test_unknown_action_is_refused(rules):
    # No rule governs this action -> default-deny REFUSE, never a silent ALLOW
    # just because nothing could be checked (fail-safe coverage guard).
    order = OrderData(
        action="unknown.action",
        requester_role="regional_manager",
        target="SOME_TARGET",
        amount=40000,
        currency="EUR",
        evidence=["invoice"],
    )
    record = evaluate(order, rules)
    assert record.decision == "REFUSE"
    assert record.checks == []
    assert "unknown.action" in record.reason

## @fn test_bind_record_is_complete(rules)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test: Bind record is complete.
#  @param rules See test body for how this fixture/argument is used.
#
def test_bind_record_is_complete(rules):
    # Every bind record must carry its identity, timestamp, target and context.
    record = evaluate(_order("regional_manager", 40000, ["invoice"]), rules)
    assert record.id
    assert record.sealed_at
    assert record.execution_target == "SAP_PAYMENT_RELEASE"
    assert record.context_snapshot["amount"] == 40000
