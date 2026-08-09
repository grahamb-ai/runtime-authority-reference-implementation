## @file authority.py
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Authority checks: does this requester have the right to perform this action at all?
#
"""Authority checks.

Authority answers a single question: *"Does this requester have the RIGHT to
perform this action at all?"* It concerns the legitimacy of the actor  never
the specifics of the particular order. A failed authority check produces a
REFUSE (a hard block, with no recourse).

Checks implemented here:
  - role_authorization  : is the requester's role permitted for this action?
  - delegation_validity : if a delegation is provided, is it still valid (not
                          expired)?
"""

from __future__ import annotations

from datetime import datetime, timezone

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

## @fn run_authority_checks(order, rules)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Run every authority check for an order and collect their outcomes.
#  @param order The OrderData being evaluated.
#  @param rules All RuleData available to check against.
#  @return A list of CheckData, one entry per authority check performed (role, delegation validity).
#
def run_authority_checks(order: OrderData, rules: list[RuleData]) -> list[CheckData]:
    """Run every authority check for 'order' and return their outcomes."""
    checks: list[CheckData] = []

    # --- role_authorization ------------------------------------------------- #
    # Collect the "authorized_role" rules that apply to this action.
    role_rules = [
        r for r in rules if r.attribute == "authorized_role" and _applies(r, order.action)
    ]
    if role_rules:
        # The set of roles the policy permits for this action.
        allowed = {str(r.value).lower() for r in role_rules}
        passed = order.requester_role.lower() in allowed
        # For the audit trail, reference the rule that authorised the requester
        # when they pass; otherwise fall back to the first role rule.
        ref = next(
            (r for r in role_rules if str(r.value).lower() == order.requester_role.lower()),
            role_rules[0],
        )
        checks.append(
            CheckData(
                name="role_authorization",
                category=CheckCategory.AUTHORITY.value,
                passed=passed,
                reason=None
                if passed
                else (
                    f"Role '{order.requester_role}' is not authorized for "
                    f"action '{order.action}'"
                ),
                rule_id=ref.id or None,
                source_excerpt=ref.source_excerpt or None,
            )
        )
    # If the policy defines no authorized-role rule for this action, there is no
    # authority constraint to enforce, so we deliberately emit no check (rather
    # than defaulting to deny). This keeps the POC permissive where the policy
    # is silent; a stricter default-deny is a one-line change if desired.

    # --- delegation_validity ------------------------------------------------ #
    # Only evaluated when the order carries a delegation with an expiry date.
    if order.delegation_expires_at is not None:
        expires = order.delegation_expires_at
        now = datetime.now(timezone.utc)
        # Compare safely whether or not the provided datetime is timezone-aware:
        # if it is naive, drop the tzinfo on 'now' to avoid a TypeError.
        if expires.tzinfo is None:
            now = now.replace(tzinfo=None)
        expired = expires < now
        checks.append(
            CheckData(
                name="delegation_validity",
                category=CheckCategory.AUTHORITY.value,
                passed=not expired,
                reason="Delegation has expired" if expired else None,
            )
        )

    return checks
