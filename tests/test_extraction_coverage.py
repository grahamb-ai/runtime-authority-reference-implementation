## @file test_extraction_coverage.py
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Exhaustive extraction coverage: every regex pattern plus documented quirks.
#
"""Exhaustive extraction coverage.

Locks down the deterministic behaviour of 'extract_rules' for every supported
pattern (A1, A2, B1, B2), the documented quirks, and the wildcard fix. Pure
tests: no database, no HTTP.

Each rule is compared as a tuple:
    (rule_type, action, attribute, value, subject, threshold)
"""

from app.engines.extractor import extract_rules

## @fn _rules(text)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test helper that runs the extractor against the shared sample policy fixture.
#  @param text See test body for how this fixture/argument is used.
#
def _rules(text):
    """Extract and normalise rules into comparable tuples."""
    out = []
    for r in extract_rules(text, "t"):
        value = tuple(r.value) if isinstance(r.value, list) else r.value
        out.append((r.rule_type, r.action, r.attribute, value, r.subject, r.threshold))
    return out


# --------------------------------------------------------------------------- #
# A1 — authorized roles
# --------------------------------------------------------------------------- #
## @fn test_a1_two_roles()
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test: A1 two roles.
#
def test_a1_two_roles():
    assert _rules("Authorized roles for payment.release: manager, director.") == [
        ("authority", "payment.release", "authorized_role", "manager", "manager", None),
        ("authority", "payment.release", "authorized_role", "director", "director", None),
    ]

## @fn test_a1_three_roles_with_and()
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test: A1 three roles with and.
#
def test_a1_three_roles_with_and():
    assert _rules("Authorized roles for payment.release: manager, director and cfo.") == [
        ("authority", "payment.release", "authorized_role", "manager", "manager", None),
        ("authority", "payment.release", "authorized_role", "director", "director", None),
        ("authority", "payment.release", "authorized_role", "cfo", "cfo", None),
    ]

## @fn test_a1_single_role()
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test: A1 single role.
#
def test_a1_single_role():
    assert _rules("Authorized roles for refund.issue: support.") == [
        ("authority", "refund.issue", "authorized_role", "support", "support", None),
    ]


# --------------------------------------------------------------------------- #
# A2 — per-role ceiling
# --------------------------------------------------------------------------- #
## @fn test_a2_comma_amount_with_currency()
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test: A2 comma amount with currency.
#
def test_a2_comma_amount_with_currency():
    assert _rules("The manager may approve payment.release up to 50,000 EUR.") == [
        ("authority", "payment.release", "max_amount", 50000.0, "manager", None),
    ]

## @fn test_a2_without_currency()
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test: A2 without currency.
#
def test_a2_without_currency():
    assert _rules("The manager may approve payment.release up to 5000.") == [
        ("authority", "payment.release", "max_amount", 5000.0, "manager", None),
    ]

## @fn test_a2_is_authorized_to_phrasing()
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test: A2 is authorized to phrasing.
#
def test_a2_is_authorized_to_phrasing():
    assert _rules("The cfo is authorized to approve payment.release up to 2,000,000 EUR.") == [
        ("authority", "payment.release", "max_amount", 2000000.0, "cfo", None),
    ]


# --------------------------------------------------------------------------- #
# B1 — conditional evidence
# --------------------------------------------------------------------------- #
## @fn test_b1_single_doc()
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test: B1 single doc.
#
def test_b1_single_doc():
    assert _rules("Any payment.release above 10,000 EUR requires invoice.") == [
        ("admissibility", "payment.release", "required_evidence", ("invoice",), None, 10000.0),
    ]

## @fn test_b1_two_docs_with_and()
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test: B1 two docs with and.
#
def test_b1_two_docs_with_and():
    assert _rules(
        "Any payment.release above 50,000 EUR must be accompanied by invoice and purchase_order."
    ) == [
        ("admissibility", "payment.release", "required_evidence",
         ("invoice", "purchase_order"), None, 50000.0),
    ]


# --------------------------------------------------------------------------- #
# B2 — unconditional evidence
# --------------------------------------------------------------------------- #
## @fn test_b2_single_doc()
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test: B2 single doc.
#
def test_b2_single_doc():
    assert _rules("refund.issue requires receipt.") == [
        ("admissibility", "refund.issue", "required_evidence", ("receipt",), None, 0.0),
    ]

## @fn test_b2_two_docs()
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test: B2 two docs.
#
def test_b2_two_docs():
    assert _rules("refund.issue requires receipt, approval_form.") == [
        ("admissibility", "refund.issue", "required_evidence",
         ("receipt", "approval_form"), None, 0.0),
    ]


# --------------------------------------------------------------------------- #
# Wildcard fix — "Authorized roles" without an action must produce NOTHING
# --------------------------------------------------------------------------- #
## @fn test_authorized_roles_without_action_extracts_nothing()
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test: Authorized roles without action extracts nothing.
#
def test_authorized_roles_without_action_extracts_nothing():
    # Previously this produced dangerous action="*" rules. It must now be skipped.
    assert _rules("Authorized roles: manager, director.") == []


## @fn test_no_wildcard_action_ever_emitted()
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test: No wildcard action ever emitted.
#
def test_no_wildcard_action_ever_emitted():
    text = """Authorized roles: baba, manager.
The manager may approve payment.release up to 100,000 EUR."""
    rules = extract_rules(text, "t")
    assert all(r.action != "*" for r in rules)
    # Only the ceiling rule survives; the action-less role sentence is dropped.
    assert len(rules) == 1
    assert rules[0].attribute == "max_amount"


# --------------------------------------------------------------------------- #
# Documented quirks (current, intentional behaviour)
# --------------------------------------------------------------------------- #
## @fn test_quirk_two_amounts_keeps_first_only()
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test: Quirk two amounts keeps first only.
#
def test_quirk_two_amounts_keeps_first_only():
    assert _rules(
        "The manager may approve payment.release up to 50,000 EUR, previously 20,000 EUR."
    ) == [
        ("authority", "payment.release", "max_amount", 50000.0, "manager", None),
    ]

## @fn test_quirk_nonsense_matches_pattern()
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test: Quirk nonsense matches pattern.
#
def test_quirk_nonsense_matches_pattern():
    # The extractor is syntactic, not semantic: nonsense that fits the grammar
    # is accepted. This is documented behaviour, asserted so it can't change
    # silently.
    assert _rules("The banana may approve fruit.salad up to 12,345 EUR.") == [
        ("authority", "fruit.salad", "max_amount", 12345.0, "banana", None),
    ]

## @fn test_quirk_complex_clause_extracts_nothing()
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test: Quirk complex clause extracts nothing.
#
def test_quirk_complex_clause_extracts_nothing():
    # Natural sentences with inserted clauses fall outside the rigid patterns
    # and yield no rules (a known limitation).
    assert _rules(
        "The regional_manager, who reports to the finance_director, may approve "
        "payment.release up to 100,000 EUR provided that targets are met."
    ) == []

## @fn test_dotted_identifier_not_split()
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test: Dotted identifier not split.
#
def test_dotted_identifier_not_split():
    # "payment.release" must survive as one token despite the dot.
    rules = extract_rules("The manager may approve payment.release up to 100 EUR.", "t")
    assert rules[0].action == "payment.release"

## @fn test_multi_sentence_paragraph_extracts_all()
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test: Multi sentence paragraph extracts all.
#
def test_multi_sentence_paragraph_extracts_all():
    text = """Authorized roles for payment.release: regional_manager, cfo.
The regional_manager may approve payment.release up to 100,000 EUR.
Any payment.release above 50,000 EUR must be accompanied by invoice and purchase_order.
The cfo may approve payment.release up to 5,000,000 EUR."""
    rules = extract_rules(text, "t")
    assert len(rules) == 5
    assert sum(1 for r in rules if r.rule_type == "authority") == 4
    assert sum(1 for r in rules if r.rule_type == "admissibility") == 1
