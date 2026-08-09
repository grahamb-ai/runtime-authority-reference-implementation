## @file admissibility.py
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Admissibility checks: is this specific order's amount and evidence acceptable?
#
"""Admissibility checks.

Admissibility answers: *"Should this SPECIFIC order proceed, given its
parameters?"* It concerns the order's context — amount, attached evidence -> not
whether the actor is fundamentally allowed to act. A failed admissibility check
produces an ESCALATE (recoverable: the response explains what is required).

Checks implemented here:
  - amount_within_limit  : is the order amount within the requester's ceiling?
  - evidence_sufficiency : are the documents required for this amount attached?

Design note — why the ceiling check lives here, not in authority
----------------------------------------------------------------
The per-role ceiling rule ('max_amount') is *stored* as an AUTHORITY-typed
rule, because it describes the actor's mandate. However, *testing a given amount*
against that ceiling is done HERE, in the admissibility phase, and yields
ESCALATE rather than REFUSE — exceeding your ceiling is the canonical
"needs higher sign-off" case, which is recoverable. Consequently, check
functions select rules by 'attribute', not by 'rule_type'.
"""

from __future__ import annotations

from app.enums import CheckCategory
from app.engines.types import CheckData, OrderData, RuleData

## @fn _applies(rule, action)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Check whether a rule governs a given action.
#  @param rule The RuleData to test.
#  @param action The action string to match against.
#  @return True if the rule applies to this action (exact match or the wildcard "*").
#
def _applies(rule: RuleData, action: str) -> bool:
    """True if 'rule' governs 'action' (exact match or the wildcard "*")."""
    return rule.action == action or rule.action == "*"

## @fn run_admissibility_checks(order, rules)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Run every admissibility check for an order and collect their outcomes.
#  @param order The OrderData being evaluated.
#  @param rules All RuleData available to check against.
#  @return A list of CheckData, one entry per admissibility check performed.
#
def run_admissibility_checks(order: OrderData, rules: list[RuleData]) -> list[CheckData]:
    """Run every admissibility check for 'order' and return their outcomes."""
    checks: list[CheckData] = []

    # --- amount_within_limit ------------------------------------------------ #
    # Gather all ceiling rules for this action, then pick the one that governs
    # this requester: prefer a ceiling tied to their exact role, else a generic
    # (subject-less) ceiling.
    limit_rules = [
        r for r in rules if r.attribute == "max_amount" and _applies(r, order.action)
    ]
    role_limit = next(
        (
            r
            for r in limit_rules
            if r.subject and r.subject.lower() == order.requester_role.lower()
        ),
        None,
    )
    generic_limit = next((r for r in limit_rules if not r.subject), None)
    applicable_limit = role_limit or generic_limit

    # Determine the effective ceiling. An explicit per-request delegation cap on
    # the order can only tighten (never loosen) the policy ceiling.
    effective_limit: float | None = None
    limit_ref: RuleData | None = applicable_limit
    if applicable_limit is not None:
        effective_limit = float(applicable_limit.value)
    if order.delegation_max_amount is not None:
        if effective_limit is None or order.delegation_max_amount < effective_limit:
            effective_limit = order.delegation_max_amount
            limit_ref = applicable_limit  # keep the rule excerpt if we have one

    # Only emit the check when there is both a ceiling and an amount to compare.
    if effective_limit is not None and order.amount is not None:
        passed = order.amount <= effective_limit
        checks.append(
            CheckData(
                name="amount_within_limit",
                category=CheckCategory.ADMISSIBILITY.value,
                passed=passed,
                reason=None
                if passed
                else (
                    f"Amount {order.amount:g} exceeds the delegated limit "
                    f"of {effective_limit:g}"
                ),
                rule_id=(limit_ref.id or None) if limit_ref else None,
                source_excerpt=(limit_ref.source_excerpt or None) if limit_ref else None,
            )
        )

    # --- evidence_sufficiency ----------------------------------------------- #
    evidence_rules = [
        r for r in rules if r.attribute == "required_evidence" and _applies(r, order.action)
    ]
    # Case-insensitive set of documents actually attached to the order.
    present = {e.lower() for e in order.evidence}
    for rule in evidence_rules:
        threshold = rule.threshold or 0.0
        amount = order.amount if order.amount is not None else 0.0
        # A conditional rule (threshold > 0) only fires above its threshold.
        if amount <= threshold and threshold > 0:
            continue

        required = [str(d).lower() for d in (rule.value or [])]
        missing = [d for d in required if d not in present]
        passed = not missing
        checks.append(
            CheckData(
                name="evidence_sufficiency",
                category=CheckCategory.ADMISSIBILITY.value,
                passed=passed,
                reason=None
                if passed
                else ("Missing required evidence: " + ", ".join(missing)),
                rule_id=rule.id or None,
                source_excerpt=rule.source_excerpt or None,
            )
        )

    return checks
