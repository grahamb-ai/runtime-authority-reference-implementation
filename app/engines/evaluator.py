## @file evaluator.py
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief The decision algorithm: composes authority and admissibility checks into one finalised decision record.
#
"""Evaluation engine : the decision algorithm.

This is the heart of the system. It composes the authority and admissibility
checks into a single finalised :class: 'BindRecordData'.

The ordering rule is strict and deliberate:

    Authority is evaluated FIRST and short-circuits.
    Admissibility is evaluated ONLY if every authority check passes.

    - any authority check fails          -> REFUSE   (admissibility NOT evaluated)
    - authority ok, admissibility fails  -> ESCALATE (with a required_action)
    - both pass                          -> ALLOW

Like the rest of the engine layer, this module is pure standard library: it
depends only on the engine dataclasses and the shared enums, so it can be
unit-tested with no database and no web server.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.enums import AuthorityState, Decision
from app.engines.admissibility import run_admissibility_checks
from app.engines.authority import run_authority_checks
from app.engines.types import BindRecordData, CheckData, OrderData, RuleData

## @fn _summarize(failed)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Join the reasons of the failed checks into one human-readable, de-duplicated string.
#  @param failed The list of CheckData entries that did not pass.
#  @return A single string combining every distinct failure reason.
#
def _summarize(failed: list[CheckData]) -> str:
    """Join the reasons of the failed checks into one human-readable string.

    Reasons are de-duplicated (preserving order) so identical checks -> e.g. from
    accidentally duplicated rules  never produce a repeated message.
    """
    reasons: list[str] = []
    for c in failed:
        if c.reason and c.reason not in reasons:
            reasons.append(c.reason)
    if not reasons:
        return "One or more checks failed"
    return "; ".join(reasons)

## @fn _derive_required_action(failed)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Translate failed admissibility checks into a concrete, actionable next step.
#  @param failed The list of failed admissibility CheckData entries.
#  @return A human-readable instruction telling the caller what to do to proceed.
#
def _derive_required_action(failed: list[CheckData]) -> str:
    """Translate failed admissibility checks into actionable next steps.

    This is what makes an ESCALATE *recoverable*: the caller is told exactly
    what to do (get senior approval, attach a document) to proceed.
    """
    names = {c.name for c in failed}
    parts: list[str] = []
    if "amount_within_limit" in names:
        parts.append("Senior approval required — amount exceeds the delegated ceiling")
    if "evidence_sufficiency" in names:
        # Reuse the specific "Missing required evidence: ..." reason, rephrased.
        missing = next(
            (c.reason for c in failed if c.name == "evidence_sufficiency" and c.reason),
            "Provide the missing supporting evidence",
        )
        parts.append(missing.replace("Missing required evidence:", "Provide before re-submitting:"))
    if not parts:
        parts.append("Manual review required")
    return " | ".join(parts)

## @fn _source_documents(checks, rules)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Collect the distinct source documents behind the checks that fired.
#  @param checks The checks produced during evaluation.
#  @param rules The rules those checks were run against.
#  @return A sorted list of the distinct source document names referenced by the checks.
#
def _source_documents(checks: list[CheckData], rules: list[RuleData]) -> list[str]:
    """Collect the distinct source documents behind the checks that fired."""
    by_id = {r.id: r.source_document for r in rules if r.id}
    docs = {by_id[c.rule_id] for c in checks if c.rule_id and c.rule_id in by_id}
    docs.discard("")
    return sorted(docs)

## @fn _has_applicable_rule(order, rules)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Determine whether at least one rule governs the order's action.
#  @param order The OrderData being evaluated.
#  @param rules All RuleData available to check against.
#  @return True if a matching (or wildcard) rule exists for this action.
#
def _has_applicable_rule(order: OrderData, rules: list[RuleData]) -> bool:
    """True if at least one rule governs the order's action.

    A rule applies when its action matches the order's action exactly, or when
    it is a wildcard ("*") rule that applies to any action.
    """
    return any(r.action == order.action or r.action == "*" for r in rules)

## @fn evaluate(order, rules)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Evaluate an order against the given rules and produce a finalised bind record.
#  @param order The proposed action to evaluate.
#  @param rules The active policy rules to evaluate it against.
#  @return A BindRecordData carrying the final ALLOW / ESCALATE / REFUSE decision and full evidence.
#
def evaluate(order: OrderData, rules: list[RuleData]) -> BindRecordData:
    """Evaluate 'order' against 'rules' and return a finalised bind record."""
    # Snapshot the order context now, so the record is self-contained for audit.
    context_snapshot = {
        "action": order.action,
        "requester_role": order.requester_role,
        "amount": order.amount,
        "currency": order.currency,
        "evidence": list(order.evidence),
    }
    record_id = str(uuid.uuid4())
    sealed_at = datetime.now(timezone.utc)

    # ---- Phase 0: COVERAGE GUARD ------------------------------------------- #
    # If no rule governs this action, it is outside the authorized perimeter.
    # We apply default-deny: an action defined nowhere in policy is REFUSED
    # rather than escalated — "anything not explicitly permitted is forbidden".
    # (Fail-safe: never allow on missing coverage.)
    if not _has_applicable_rule(order, rules):
        return BindRecordData(
            id=record_id,
            decision=Decision.REFUSE.value,
            authority_state=AuthorityState.INVALID.value,
            reason=f"No policy rules found for action '{order.action}'",
            required_action=None,
            execution_target=order.target,
            checks=[],
            context_snapshot=context_snapshot,
            source_documents=[],
            sealed_at=sealed_at,
        )

    # ---- Phase 1: AUTHORITY ------------------------------------------------- #
    authority_checks = run_authority_checks(order, rules)
    failed_authority = [c for c in authority_checks if not c.passed]

    if failed_authority:
        # Distinguish an expired delegation from a plain role rejection so the
        # authority_state is precise for auditors.
        delegation_expired = any(
            c.name == "delegation_validity" and not c.passed for c in failed_authority
        )
        state = AuthorityState.EXPIRED if delegation_expired else AuthorityState.INVALID
        return BindRecordData(
            id=record_id,
            decision=Decision.REFUSE.value,
            authority_state=state.value,
            reason=_summarize(failed_authority),
            required_action=None,               # REFUSE has no recourse
            execution_target=order.target,
            checks=authority_checks,            # admissibility intentionally skipped
            context_snapshot=context_snapshot,
            source_documents=_source_documents(authority_checks, rules),
            sealed_at=sealed_at,
        )

    # ---- Phase 2: ADMISSIBILITY (only reached if authority passed) ---------- #
    admissibility_checks = run_admissibility_checks(order, rules)
    all_checks = authority_checks + admissibility_checks
    failed_admissibility = [c for c in admissibility_checks if not c.passed]

    if failed_admissibility:
        return BindRecordData(
            id=record_id,
            decision=Decision.ESCALATE.value,
            authority_state=AuthorityState.VALID.value,
            reason=_summarize(failed_admissibility),
            required_action=_derive_required_action(failed_admissibility),
            execution_target=order.target,
            checks=all_checks,
            context_snapshot=context_snapshot,
            source_documents=_source_documents(all_checks, rules),
            sealed_at=sealed_at,
        )

    # ---- Both phases passed -> ALLOW --------------------------------------- #
    return BindRecordData(
        id=record_id,
        decision=Decision.ALLOW.value,
        authority_state=AuthorityState.VALID.value,
        reason="All authority and admissibility checks passed",
        required_action=None,
        execution_target=order.target,
        checks=all_checks,
        context_snapshot=context_snapshot,
        source_documents=_source_documents(all_checks, rules),
        sealed_at=sealed_at,
    )
