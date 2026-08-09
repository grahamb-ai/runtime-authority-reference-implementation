## @file schemas.py
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Pydantic v2 schemas: the HTTP request/response contracts and OpenAPI documentation source.
#
"""Pydantic v2 schemas : the HTTP request/response contracts.

These models define exactly what the API accepts and returns, drive automatic
validation, and generate the OpenAPI/Swagger documentation. They live at the
HTTP boundary only; the engines never import them.

Two conversion helpers bridge to the engine layer:
  - 'AuthorityEnvelope.to_order_data' : request  -> engine input
  - 'BindRecord.from_data'            : engine output -> response
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.enums import AuthorityState, CheckCategory, Decision
from app.engines.types import BindRecordData, OrderData


# --------------------------------------------------------------------------- #
# Request: an order submitted for evaluation (the "authority envelope")
# --------------------------------------------------------------------------- #
class Requester(BaseModel):
    """Who is submitting the order."""

    id: str | None = None
    role: str  # the only required field -> authority hinges on the role


class Delegation(BaseModel):
    """An optional per-request delegation cap declared by the requester.

    Note: this does NOT carry an expiry. A server-side delegation registry
    that resolved expiry independently of the client's claim was evaluated and
    then removed; no replacement is wired up yet, so 'delegation_validity'
    (see engines/authority.py) is currently dormant. It never fires,
    because nothing populates 'OrderData.delegation_expires_at'. It was
    deliberately never accepted directly from the client either: a
    requester's own submission cannot be trusted to self-declare when its own
    mandate expires, since it could simply always claim a future date.
    'max_amount' remains safe to accept from the client because it can only
    tighten the effective ceiling, never loosen it (the evaluator takes the
    stricter of the policy limit and this value).
    """

    granted_by: str | None = None
    max_amount: float | None = None  # a per-request spending cap (tightening only)


class AuthorityEnvelope(BaseModel):
    """The full incoming payload describing a proposed action."""

    action: str
    target: str = ""
    requester: Requester
    delegation: Delegation | None = None
    # Free-form context; 'amount' and 'currency' are the keys the engine reads.
    context: dict[str, Any] = Field(default_factory=dict)
    evidence: list[str] = Field(default_factory=list)

    # A concrete example so Swagger shows a ready-to-send body on /docs.
    model_config = {
        "json_schema_extra": {
            "example": {
                "action": "payment.release",
                "target": "SAP_PAYMENT_RELEASE",
                "requester": {"id": "user-42", "role": "regional_manager"},
                "delegation": {"granted_by": "cfo", "max_amount": 100000},
                "context": {"amount": 250000, "currency": "EUR"},
                "evidence": ["invoice-44721"],
            }
        }
    }

    ## @fn to_order_data(self)
    #  @author FlowSignal Dev Team
    #  @version 0.1
    #  @date 25 July 2026
    #  @brief Flatten this HTTP request envelope into the engine's OrderData.
    #  @param self The incoming AuthorityEnvelope to convert.
    #  @return An OrderData ready to be passed to evaluate().
    #
    def to_order_data(self) -> OrderData:
        """Flatten this HTTP envelope into the engine's :class:'OrderData'.

        'delegation_expires_at' is intentionally never set here :  see the
        note on :class:Delegation for why (dormant: nothing currently
        supplies a trustworthy expiry, client-side or server-side).
        """
        return OrderData(
            action=self.action,
            requester_role=self.requester.role,
            target=self.target,
            amount=self.context.get("amount"),
            currency=self.context.get("currency"),
            delegation_max_amount=self.delegation.max_amount if self.delegation else None,
            evidence=list(self.evidence),
        )


# --------------------------------------------------------------------------- #
# Response: the finalised bind record
# --------------------------------------------------------------------------- #
class Check(BaseModel):
    """One check's outcome, as exposed over HTTP (mirrors 'CheckData')."""

    name: str
    category: CheckCategory
    passed: bool
    reason: str | None = None
    rule_id: str | None = None
    source_excerpt: str | None = None


class BindRecord(BaseModel):
    """The full evaluation result returned to the caller."""

    id: str
    decision: Decision
    authority_state: AuthorityState
    reason: str
    required_action: str | None = None
    execution_target: str
    checks: list[Check] = Field(default_factory=list)
    context_snapshot: dict[str, Any] = Field(default_factory=dict)
    source_documents: list[str] = Field(default_factory=list)
    sealed_at: datetime

    @classmethod
    ## @fn from_data(cls, data)
    #  @author FlowSignal Dev Team
    #  @version 0.1
    #  @date 25 July 2026
    #  @brief Build the HTTP response model from the engine's finalised bind record.
    #  @param cls The BindRecord class itself.
    #  @param data The BindRecordData produced by evaluate().
    #  @return A BindRecord ready to be serialized as the API response.
    #
    def from_data(cls, data: BindRecordData) -> "BindRecord":
        """Build the HTTP response model from the engine's bind record.

        Plain string values coming out of the engine are validated back into
        their enums here (Decision(...), AuthorityState(...),
        CheckCategory(...)), which also guarantees they are well-formed.
        """
        return cls(
            id=data.id,
            decision=Decision(data.decision),
            authority_state=AuthorityState(data.authority_state),
            reason=data.reason,
            required_action=data.required_action,
            execution_target=data.execution_target,
            checks=[
                Check(
                    name=c.name,
                    category=CheckCategory(c.category),
                    passed=c.passed,
                    reason=c.reason,
                    rule_id=c.rule_id,
                    source_excerpt=c.source_excerpt,
                )
                for c in data.checks
            ],
            context_snapshot=data.context_snapshot,
            source_documents=data.source_documents,
            sealed_at=data.sealed_at,
        )


# --------------------------------------------------------------------------- #
# Response: summary returned after uploading a policy document
# --------------------------------------------------------------------------- #
class ExtractedRule(BaseModel):
    """A single extracted rule, echoed back after an upload for transparency."""

    rule_type: str
    action: str
    attribute: str
    operator: str
    value: Any
    subject: str | None = None
    threshold: float | None = None
    source_excerpt: str


class UploadSummary(BaseModel):
    """The result of parsing an uploaded policy document."""

    source_document: str
    authority_rules: int
    admissibility_rules: int
    total_rules: int
    rules: list[ExtractedRule] = Field(default_factory=list)
