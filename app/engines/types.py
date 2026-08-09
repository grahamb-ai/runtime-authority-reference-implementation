## @file types.py
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Plain standard-library dataclasses used internally by the pure engine layer.
#
"""Plain dataclasses used internally by the engine layer.

Design rule (the backbone of the whole project)
------------------------------------------------
The engines -> parser, extractor, authority, admissibility, evaluator : operate
ONLY on these standard-library dataclasses. They never import FastAPI, Pydantic,
or SQLModel. This keeps the core decision logic:
  - transport-agnostic (no HTTP concepts leak in),
  - storage-agnostic (no ORM concepts leak in),
  - trivially unit-testable (no server, no database required).

The surrounding layers convert to/from these types at their boundaries:

    HTTP in  : AuthorityEnvelope (Pydantic)  -> OrderData        (schemas.to_order_data)
    DB  in   : Rule (SQLModel)               -> RuleData         (Rule.to_data)
    engine   : evaluate(OrderData, [RuleData]) -> BindRecordData
    DB  out  : BindRecordData                -> Order (SQLModel) (Order.from_bind_record)
    HTTP out : BindRecordData                -> BindRecord (Pydantic) (BindRecord.from_data)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class RuleData:
    """A single policy rule, decoupled from its database row.

    One row in the rule` table maps to one 'RuleData'. The shape is
    intentionally generic so a handful of fields can describe every rule kind:

        authorized_role  : value = a role name,            operator = "in"
        max_amount       : value = a number, subject=role, operator = "<="
        required_evidence: value = list[str], threshold=N, operator = "requires"
    """

    id: str                       # DB primary key (empty string before persistence)
    rule_type: str                # RuleType value: "authority" | "admissibility"
    action: str                   # action this rule governs, or "*" for any
    attribute: str                # "authorized_role" | "max_amount" | "required_evidence"
    operator: str                 # "in" | "<=" | "requires"
    value: Any                    # str | float | list, depending on ``attribute``
    subject: str | None = None    # e.g. the role a max_amount ceiling applies to
    threshold: float | None = None  # amount above which an evidence rule triggers
    source_document: str = ""     # originating filename (audit)
    source_excerpt: str = ""      # exact text the rule was parsed from (audit)


@dataclass
class OrderData:
    """A proposed action submitted for evaluation.

    This is the engine-facing view of an incoming request, flattened from the
    richer 'AuthorityEnvelope' used at the HTTP boundary.
    """

    action: str                                  # e.g. "payment.release"
    requester_role: str                          # role of whoever submits the order
    target: str = ""                             # downstream system the action targets
    amount: float | None = None                  # monetary amount, if any
    currency: str | None = None                  # ISO currency label, informational
    delegation_max_amount: float | None = None   # explicit per-request delegation cap
    delegation_expires_at: datetime | None = None  # delegation expiry, if provided
    evidence: list[str] = field(default_factory=list)  # attached supporting documents


@dataclass
class CheckData:
    """The outcome of one individual rule check, with its audit trail.

    Each check records not only pass/fail but *which* rule produced it and the
    original document excerpt, so a bind record is fully self-explaining.
    """

    name: str                       # e.g. "role_authorization", "amount_within_limit"
    category: str                   # CheckCategory value: "authority" | "admissibility"
    passed: bool                    # did this check pass?
    reason: str | None = None       # human-readable failure reason (None if passed)
    rule_id: str | None = None      # id of the rule that drove the check (audit)
    source_excerpt: str | None = None  # policy text the rule came from (audit)


@dataclass
class BindRecordData:
    
    """The finalised result of an evaluation -> the engine's final output.

    The record captures the outcome, reasoning, checks, a snapshot of the order
    context, source documents, and the decision timestamp.

    The field name ``sealed_at`` is retained for compatibility with the current
    API and evidence artefacts. In this reference implementation, it records when
    the decision was finalised; it does not imply cryptographic signing or
    tamper-evident sealing.
    
    """

    id: str                          # unique record id (UUID4)
    decision: str                    # Decision value: ALLOW | ESCALATE | REFUSE
    authority_state: str             # AuthorityState value
    reason: str                      # summary of why this decision was reached
    execution_target: str            # the order's target system
    sealed_at: datetime              # when the decision was made (UTC)
    required_action: str | None = None            # what to do next (ESCALATE only)
    checks: list[CheckData] = field(default_factory=list)       # every check run
    context_snapshot: dict[str, Any] = field(default_factory=dict)  # order at decision time
    source_documents: list[str] = field(default_factory=list)   # docs the rules came from
