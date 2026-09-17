"""ASVH HARDEN-010 — hostile multi-source authority conflict cases.

Frozen before remediation.

Question under attack:
What happens when individually fresh authority sources disagree immediately
before consequence formation?

Safety proposition:
No aggregate or lower-precedence positive assertion may convert an unresolved
or prohibitive authoritative conflict into ALLOW.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Standing:
    source: str
    sequence: int
    age_seconds: int
    status: str


def naive_fresh_majority(*standings: Standing) -> str:
    """Deliberately vulnerable comparator for failure-first evidence."""
    fresh = [s for s in standings if 0 <= s.age_seconds <= 30]
    positive = sum(s.status in {"AUTHORISED", "VALID", "CLEAR"} for s in fresh)
    return "ALLOW" if positive >= 2 else "PREVENTED"


def test_h10_005_fresh_registry_revoked_org_valid_aggregate_authorised_must_not_allow():
    registry = Standing("product_registry", 50, 0, "REVOKED")
    organisation = Standing("deployment_authority", 77, 0, "VALID")
    aggregate = Standing("HC-STATE-01", 1001, 0, "AUTHORISED")
    assert naive_fresh_majority(registry, organisation, aggregate) != "ALLOW"


def test_h10_006_fresh_registry_suspended_org_valid_aggregate_authorised_must_not_allow():
    registry = Standing("product_registry", 51, 1, "SUSPENDED")
    organisation = Standing("deployment_authority", 78, 1, "VALID")
    aggregate = Standing("HC-STATE-01", 1002, 1, "AUTHORISED")
    assert naive_fresh_majority(registry, organisation, aggregate) != "ALLOW"


def test_h10_007_unknown_registry_cannot_be_outvoted_by_two_positive_sources():
    registry = Standing("product_registry", 52, 0, "UNKNOWN")
    organisation = Standing("deployment_authority", 79, 0, "VALID")
    aggregate = Standing("HC-STATE-01", 1003, 0, "AUTHORISED")
    assert naive_fresh_majority(registry, organisation, aggregate) != "ALLOW"


def test_h10_008_higher_aggregate_sequence_cannot_outvote_authoritative_revocation():
    registry = Standing("product_registry", 53, 0, "REVOKED")
    organisation = Standing("deployment_authority", 80, 0, "VALID")
    aggregate = Standing("HC-STATE-01", 999999, 0, "AUTHORISED")
    assert aggregate.sequence > registry.sequence
    assert naive_fresh_majority(registry, organisation, aggregate) != "ALLOW"
