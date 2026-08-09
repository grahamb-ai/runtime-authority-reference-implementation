## @file test_decision_coverage.py
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Exhaustive decision coverage: the full ALLOW / ESCALATE / REFUSE matrix.
#
"""Exhaustive decision coverage : the full ALLOW / ESCALATE / REFUSE matrix.

Locks down every branch of the decision engine against one fixed policy, so the
attribution of outcomes cannot regress silently. Pure tests: no database, no
HTTP. Includes boundary values (exactly at each threshold) and the coverage
guard for unknown actions.
"""

import pytest

from app.engines.evaluator import evaluate
from app.engines.extractor import extract_rules
from app.engines.types import OrderData

# Fixed policy used by every test in this module:
#   payment.release — roles: regional_manager (<=100k), finance_director (<=500k), cfo (<=2M)
#   payment.release above 50,000 EUR requires invoice + purchase_order
POLICY = """Authorized roles for payment.release: regional_manager, finance_director, cfo.
The regional_manager may approve payment.release up to 100,000 EUR.
The finance_director may approve payment.release up to 500,000 EUR.
The cfo may approve payment.release up to 2,000,000 EUR.
Any payment.release above 50,000 EUR must be accompanied by invoice and purchase_order."""


@pytest.fixture
## @fn rules()
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Pytest fixture providing a fixed set of extracted rules for the tests in this file.
#
def rules():
    rs = extract_rules(POLICY, "policy")
    for i, r in enumerate(rs):
        r.id = f"rule-{i}"
    return rs

## @fn _decide(rules, role, amount, evidence, action)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test helper that builds an order and runs it through evaluate() in one call.
#  @param rules See test body for how this fixture/argument is used.
#  @param role See test body for how this fixture/argument is used.
#  @param amount See test body for how this fixture/argument is used.
#  @param evidence See test body for how this fixture/argument is used.
#  @param action See test body for how this fixture/argument is used.
#
def _decide(rules, role, amount, evidence, action="payment.release"):
    order = OrderData(
        action=action, requester_role=role, target="T",
        amount=amount, currency="EUR", evidence=evidence,
    )
    return evaluate(order, rules)


# --------------------------------------------------------------------------- #
# REFUSE — authority fails (short-circuits, admissibility never evaluated)
# --------------------------------------------------------------------------- #
## @fn test_refuse_unauthorized_role_small_amount(rules)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test: Refuse unauthorized role small amount.
#  @param rules See test body for how this fixture/argument is used.
#
def test_refuse_unauthorized_role_small_amount(rules):
    r = _decide(rules, "intern", 10000, [])
    assert r.decision == "REFUSE"
    assert [c.name for c in r.checks] == ["role_authorization"]
    assert r.required_action is None

## @fn test_refuse_unauthorized_role_even_with_everything_else_valid(rules)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test: Refuse unauthorized role even with everything else valid.
#  @param rules See test body for how this fixture/argument is used.
#
def test_refuse_unauthorized_role_even_with_everything_else_valid(rules):
    # Big amount + full evidence must NOT rescue an unauthorized role.
    r = _decide(rules, "intern", 999999, ["invoice", "purchase_order"])
    assert r.decision == "REFUSE"
    # admissibility must not have run
    assert all(c.category == "authority" for c in r.checks)

## @fn test_refuse_empty_role(rules)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test: Refuse empty role.
#  @param rules See test body for how this fixture/argument is used.
#
def test_refuse_empty_role(rules):
    assert _decide(rules, "", 10000, []).decision == "REFUSE"


# --------------------------------------------------------------------------- #
# ALLOW — both authority and admissibility pass
# --------------------------------------------------------------------------- #
## @fn test_allow_under_ceiling_under_evidence_threshold(rules)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test: Allow under ceiling under evidence threshold.
#  @param rules See test body for how this fixture/argument is used.
#
def test_allow_under_ceiling_under_evidence_threshold(rules):
    r = _decide(rules, "regional_manager", 40000, [])
    assert r.decision == "ALLOW"
    assert r.required_action is None

## @fn test_allow_over_threshold_with_full_evidence(rules)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test: Allow over threshold with full evidence.
#  @param rules See test body for how this fixture/argument is used.
#
def test_allow_over_threshold_with_full_evidence(rules):
    assert _decide(rules, "regional_manager", 80000, ["invoice", "purchase_order"]).decision == "ALLOW"

## @fn test_allow_finance_director_higher_ceiling(rules)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test: Allow finance director higher ceiling.
#  @param rules See test body for how this fixture/argument is used.
#
def test_allow_finance_director_higher_ceiling(rules):
    assert _decide(rules, "finance_director", 400000, ["invoice", "purchase_order"]).decision == "ALLOW"


# --------------------------------------------------------------------------- #
# ESCALATE — authority ok, admissibility fails
# --------------------------------------------------------------------------- #
## @fn test_escalate_over_ceiling(rules)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test: Escalate over ceiling.
#  @param rules See test body for how this fixture/argument is used.
#
def test_escalate_over_ceiling(rules):
    r = _decide(rules, "regional_manager", 250000, ["invoice", "purchase_order"])
    assert r.decision == "ESCALATE"
    assert any(c.name == "amount_within_limit" and not c.passed for c in r.checks)

## @fn test_escalate_missing_all_evidence(rules)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test: Escalate missing all evidence.
#  @param rules See test body for how this fixture/argument is used.
#
def test_escalate_missing_all_evidence(rules):
    r = _decide(rules, "regional_manager", 80000, [])
    assert r.decision == "ESCALATE"
    assert any(c.name == "evidence_sufficiency" and not c.passed for c in r.checks)

## @fn test_escalate_missing_one_evidence(rules)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test: Escalate missing one evidence.
#  @param rules See test body for how this fixture/argument is used.
#
def test_escalate_missing_one_evidence(rules):
    # Has invoice but not purchase_order -> still ESCALATE.
    r = _decide(rules, "regional_manager", 80000, ["invoice"])
    assert r.decision == "ESCALATE"

## @fn test_escalate_over_ceiling_and_missing_evidence(rules)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test: Escalate over ceiling and missing evidence.
#  @param rules See test body for how this fixture/argument is used.
#
def test_escalate_over_ceiling_and_missing_evidence(rules):
    r = _decide(rules, "regional_manager", 250000, [])
    assert r.decision == "ESCALATE"
    failed = {c.name for c in r.checks if not c.passed}
    assert "amount_within_limit" in failed
    assert "evidence_sufficiency" in failed


# --------------------------------------------------------------------------- #
# Coverage guard — unknown action is refused (default-deny)
# --------------------------------------------------------------------------- #
## @fn test_unknown_action_is_refused(rules)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test: Unknown action is refused.
#  @param rules See test body for how this fixture/argument is used.
#
def test_unknown_action_is_refused(rules):
    r = _decide(rules, "regional_manager", 40000, ["invoice", "purchase_order"], action="mystery.action")
    assert r.decision == "REFUSE"
    assert r.checks == []
    assert "mystery.action" in r.reason


# --------------------------------------------------------------------------- #
# Boundary values — exactly at each threshold
# --------------------------------------------------------------------------- #
## @fn test_boundary_exactly_at_ceiling_allows(rules)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test: Boundary exactly at ceiling allows.
#  @param rules See test body for how this fixture/argument is used.
#
def test_boundary_exactly_at_ceiling_allows(rules):
    assert _decide(rules, "regional_manager", 100000, ["invoice", "purchase_order"]).decision == "ALLOW"

## @fn test_boundary_one_over_ceiling_escalates(rules)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test: Boundary one over ceiling escalates.
#  @param rules See test body for how this fixture/argument is used.
#
def test_boundary_one_over_ceiling_escalates(rules):
    assert _decide(rules, "regional_manager", 100001, ["invoice", "purchase_order"]).decision == "ESCALATE"

## @fn test_boundary_exactly_at_evidence_threshold_needs_no_evidence(rules)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test: Boundary exactly at evidence threshold needs no evidence.
#  @param rules See test body for how this fixture/argument is used.
#
def test_boundary_exactly_at_evidence_threshold_needs_no_evidence(rules):
    # 50,000 is NOT above 50,000, so the evidence rule does not fire.
    assert _decide(rules, "regional_manager", 50000, []).decision == "ALLOW"

## @fn test_boundary_one_over_evidence_threshold_requires_evidence(rules)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test: Boundary one over evidence threshold requires evidence.
#  @param rules See test body for how this fixture/argument is used.
#
def test_boundary_one_over_evidence_threshold_requires_evidence(rules):
    assert _decide(rules, "regional_manager", 50001, []).decision == "ESCALATE"
