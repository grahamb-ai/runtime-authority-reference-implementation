## @file order.py
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Database model for evaluated orders (the orders table): the persisted form of a bind record.
#
"""Database model for evaluated orders (the orders table).

An 'Order' row is the persisted form of a sealed :class:`BindRecordData`: it
stores both what was submitted and the decision that was reached, so any past
evaluation can be retrieved later as an audit record.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel

from app.engines.types import BindRecordData

## @fn _utcnow()
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Return the current UTC time, timezone-aware.
#  @return A timezone-aware datetime set to now, in UTC.
#
def _utcnow() -> datetime:
    """Timezone-aware UTC 'now' (used as a default factory)."""
    return datetime.now(timezone.utc)


class Order(SQLModel, table=True):
    """A submitted order together with the sealed decision."""

    __tablename__ = "orders"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)

    # --- what was submitted ------------------------------------------------- #
    action: str
    target: str = ""
    requester_role: str = ""
    # JSON columns for the free-form parts of the request.
    context: dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    evidence: list[str] = Field(default=[], sa_column=Column(JSON))

    # --- the sealed decision ------------------------------------------------ #
    decision: str = ""          # Decision value
    authority_state: str = ""   # AuthorityState value
    reason: str = ""
    required_action: str | None = None
    # The full list of checks, stored as JSON for a complete audit trail.
    checks: list[dict[str, Any]] = Field(default=[], sa_column=Column(JSON))
    source_documents: list[str] = Field(default=[], sa_column=Column(JSON))
    sealed_at: datetime = Field(default_factory=_utcnow)

    @classmethod
    ## @fn from_bind_record(cls, record)
    #  @author FlowSignal Dev Team
    #  @version 0.1
    #  @date 25 July 2026
    #  @brief Build a persistable database row from an evaluator bind record.
    #  @param cls The Order class itself.
    #  @param record The sealed BindRecordData produced by evaluate().
    #  @return An Order instance ready to be added to the database session.
    #
    def from_bind_record(cls, record: BindRecordData) -> "Order":
        """Build a persistable row from a bind record produced by the evaluator.

        The check dataclasses are flattened to plain dicts (``__dict__``) so they
        fit the JSON column; ``action``/``requester_role`` are pulled back out of
        the context snapshot for convenient top-level querying.
        """
        return cls(
            id=record.id,
            action=record.context_snapshot.get("action", ""),
            target=record.execution_target,
            requester_role=record.context_snapshot.get("requester_role", ""),
            context=record.context_snapshot,
            evidence=record.context_snapshot.get("evidence", []),
            decision=record.decision,
            authority_state=record.authority_state,
            reason=record.reason,
            required_action=record.required_action,
            checks=[check.__dict__ for check in record.checks],
            source_documents=record.source_documents,
            sealed_at=record.sealed_at,
        )
