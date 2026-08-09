## @file orders.py
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Orders router: evaluate orders and retrieve previously finalised bind records.
#
"""Orders router : evaluate orders and retrieve finalised bind records.

Exposes three endpoints under /api/v1/orders:
  - POST /evaluate : evaluate an order, persist the result, return it
  - POST /assess   : same evaluation but WITHOUT persisting (a dry-run)
  - GET  /{id}     : fetch a previously persisted bind record

This router composes the transport (FastAPI), the database (load rules / save
orders), and the pure evaluator.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.engines.evaluator import evaluate
from app.models.order import Order
from app.models.rule import Rule
from app.models.schemas import AuthorityEnvelope, BindRecord

router = APIRouter(prefix="/api/v1/orders", tags=["orders"])

## @fn _load_rules(session)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Load every rule currently in the database as engine-facing RuleData.
#  @param session The active database session.
#  @return A list of RuleData ready to be passed to evaluate().
#
def _load_rules(session: Session) -> list:
    """Load every rule from the database as engine-facing RuleData"""
    rows = session.exec(select(Rule)).all()
    return [row.to_data() for row in rows]


@router.post("/evaluate", response_model=BindRecord, summary="Evaluate an order and persist the result")
## @fn evaluate_order(envelope, session)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Evaluate an order, persist the finalised bind record, and return it.
#  @param envelope The incoming HTTP request body describing the proposed action.
#  @param session The active database session.
#  @return The BindRecord describing the decision that was reached.
#
def evaluate_order(
    envelope: AuthorityEnvelope,
    session: Session = Depends(get_session),
) -> BindRecord:
    """Evaluate the order, persist the finalised bind record, and return it."""
    rules = _load_rules(session)
    # Convert HTTP -> engine, run the pure evaluator, then persist.
    record = evaluate(envelope.to_order_data(), rules)
    session.add(Order.from_bind_record(record))
    session.commit()
    return BindRecord.from_data(record)


@router.post("/assess", response_model=BindRecord, summary="Dry-run evaluation (not persisted)")
## @fn assess_order(envelope, session)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Evaluate an order WITHOUT persisting anything, a dry-run preview.
#  @param envelope The incoming HTTP request body describing the proposed action.
#  @param session The active database session.
#  @return The BindRecord describing the decision that would be reached (not saved).
#
def assess_order(
    envelope: AuthorityEnvelope,
    session: Session = Depends(get_session),
) -> BindRecord:
    """Evaluate the order WITHOUT persisting anything — a preview / dry-run.

    Identical decision logic to /evaluate; only the persistence side effect is
    omitted. Useful to preview an outcome before committing to it.
    """
    rules = _load_rules(session)
    record = evaluate(envelope.to_order_data(), rules)
    return BindRecord.from_data(record)


@router.get("/{order_id}", response_model=BindRecord, summary="Retrieve a finalised bind record")
## @fn get_order(order_id, session)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Fetch a previously finalised bind record by its id.
#  @param order_id The identifier of the bind record to retrieve.
#  @param session The active database session.
#  @return The matching BindRecord; the endpoint responds 404 if the id is unknown.
#
def get_order(order_id: str, session: Session = Depends(get_session)) -> BindRecord:
    """Fetch a previously finalised bind record by id, or 404 if unknown."""
    order = session.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail=f"Order '{order_id}' not found")

    # Rehydrate the stored JSON checks into the response shape.
    checks = [
        {
            "name": c.get("name"),
            "category": c.get("category"),
            "passed": c.get("passed"),
            "reason": c.get("reason"),
            "rule_id": c.get("rule_id"),
            "source_excerpt": c.get("source_excerpt"),
        }
        for c in (order.checks or [])
    ]
    return BindRecord(
        id=order.id,
        decision=order.decision,
        authority_state=order.authority_state,
        reason=order.reason,
        required_action=order.required_action,
        execution_target=order.target,
        checks=checks,
        context_snapshot=order.context,
        source_documents=order.source_documents,
        sealed_at=order.sealed_at,
    )
