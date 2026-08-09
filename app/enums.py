## @file enums.py
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Shared, dependency-free enumerations used across the HTTP, database, and engine layers.
#
"""Shared enumerations for the whole application.

Why a dedicated, dependency-free module?
    These enums are referenced from three very different layers:
      - the Pydantic schemas (HTTP boundary),
      - the SQLModel tables (database boundary),
      - the pure-Python engines (business logic).
    Keeping them in a single module that imports nothing but the standard
    library guarantees every layer shares one source of truth and that the
    engine layer stays free of third-party dependencies.

Every enum subclasses 'str' so that:
      - its members compare equal to plain strings (e.g. Decision.ALLOW == "ALLOW"),
      - it serialises to JSON as its string value with no custom encoder,
      - it can be stored directly in a database text/JSON column.
"""

from enum import Enum


class RuleType(str, Enum):
    """The two families of rules extracted from a policy document."""

    AUTHORITY = "authority"          # "who is allowed to do this"
    ADMISSIBILITY = "admissibility"  # "under what conditions may it happen"


class CheckCategory(str, Enum):
    """The dimension a single check belongs to.

    Mirrors 'RuleType' but describes an evaluated check rather than a stored
    rule. Kept separate so the two concepts can diverge later without churn.
    """

    AUTHORITY = "authority"
    ADMISSIBILITY = "admissibility"


class Decision(str, Enum):
    """The final outcome returned for an evaluated order."""

    ALLOW = "ALLOW"        # authority AND admissibility both passed
    ESCALATE = "ESCALATE"  # authority passed, admissibility failed (recoverable)
    REFUSE = "REFUSE"      # authority failed (hard block, no recourse)


class AuthorityState(str, Enum):
    """A finer-grained status of the requester's authority.

    Reported alongside the decision so an auditor can tell *why* authority was
    or was not satisfied.
    """

    VALID = "VALID"      # the actor's mandate is legitimate
    INVALID = "INVALID"  # role not authorized for the action
    EXPIRED = "EXPIRED"  # a delegation was present but past its expiry date
