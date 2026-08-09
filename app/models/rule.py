## @file rule.py
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Database model for extracted rules (the rules table): the persisted form of a RuleData.
#
"""Database model for extracted rules (the 'rules' table).

A 'Rule' is the persisted form of a :class:'RuleData'. This class owns the
mapping in both directions:
  - 'to_data()'   : row  -> engine dataclass (used when loading rules to evaluate)
  - 'from_data()' : dataclass -> row        (used when saving extracted rules)

This keeps the ORM concern in the model and the engines free of SQLModel.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel

from app.engines.types import RuleData

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


class Rule(SQLModel, table=True):
    """A single rule extracted from a policy document."""

    __tablename__ = "rules"

    # Server-side default id so freshly extracted rules get a stable UUID on insert.
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    rule_type: str                      # RuleType value
    action: str                         # action governed, or "*"
    attribute: str                      # authorized_role | max_amount | required_evidence
    operator: str                       # in | <= | requires
    # ``value`` is heterogeneous (str | float | list), so it is stored as JSON.
    value: Any = Field(sa_column=Column(JSON))
    subject: str | None = None          # e.g. the role a ceiling applies to
    threshold: float | None = None      # amount above which an evidence rule fires
    source_document: str = ""           # originating filename (audit)
    source_excerpt: str = ""            # exact policy text (audit)
    created_at: datetime = Field(default_factory=_utcnow)

    ## @fn to_data(self)
    #  @author FlowSignal Dev Team
    #  @version 0.1
    #  @date 25 July 2026
    #  @brief Convert this database row back into the engine's plain RuleData dataclass.
    #  @param self The Rule row to convert.
    #  @return The equivalent RuleData object, ready for use by the pure engine layer.
    #
    def to_data(self) -> RuleData:
        """Convert this database row into the engine's plain dataclass."""
        return RuleData(
            id=self.id,
            rule_type=self.rule_type,
            action=self.action,
            attribute=self.attribute,
            operator=self.operator,
            value=self.value,
            subject=self.subject,
            threshold=self.threshold,
            source_document=self.source_document,
            source_excerpt=self.source_excerpt,
        )

    @classmethod
    ## @fn from_data(cls, data)
    #  @author FlowSignal Dev Team
    #  @version 0.1
    #  @date 25 July 2026
    #  @brief Build a persistable database row from an extracted RuleData.
    #  @param cls The Rule class itself.
    #  @param data The RuleData produced by the extractor.
    #  @return A Rule instance ready to be added to the database session.
    #
    def from_data(cls, data: RuleData) -> "Rule":
        """Build a persistable row from an extracted :class:`RuleData`.

        The id is intentionally NOT copied — the extractor leaves it blank and
        the database assigns a fresh UUID via ``default_factory`` on insert.
        """
        return cls(
            rule_type=data.rule_type,
            action=data.action,
            attribute=data.attribute,
            operator=data.operator,
            value=data.value,
            subject=data.subject,
            threshold=data.threshold,
            source_document=data.source_document,
            source_excerpt=data.source_excerpt,
        )
