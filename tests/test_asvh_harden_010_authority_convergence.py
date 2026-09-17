"""ASVH HARDEN-010 — Authority Dependency Convergence.

Hostile tests are intentionally frozen before remediation.

Proposition under test:
A fresh aggregate standing snapshot MUST NOT be sufficient for consequence
formation where a required underlying authoritative dependency has advanced
to a conflicting, withdrawn, superseded, or indeterminate state.

These tests model the seam between an aggregate present-standing observation
and independently authoritative dependency state. They are expected to expose
any implementation that treats aggregate freshness as authoritative
convergence.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class AggregateStanding:
    sequence: int
    age_seconds: int
    product_authorised: bool
    workflow_valid: bool = True
    monitoring_clear: bool = True
    policy_version: str = "1.0"


@dataclass(frozen=True)
class ProductRegistryStanding:
    sequence: int
    status: str  # AUTHORISED / SUSPENDED / REVOKED / UNKNOWN


def aggregate_only_precommit(snapshot: AggregateStanding) -> str:
    """Deliberately represents the pre-HARDEN-010 failure hypothesis.

    It validates only the fresh aggregate snapshot. This is not remediation;
    it exists so the hostile finding is executable and preserved.
    """
    if snapshot.age_seconds < 0 or snapshot.age_seconds > 30:
        return "PREVENTED"
    if not snapshot.product_authorised:
        return "PREVENTED"
    if not snapshot.workflow_valid or not snapshot.monitoring_clear:
        return "PREVENTED"
    return "ALLOW"


def test_h10_001_fresh_aggregate_must_not_override_registry_suspension():
    aggregate = AggregateStanding(sequence=101, age_seconds=0, product_authorised=True)
    registry = ProductRegistryStanding(sequence=44, status="SUSPENDED")
    assert registry.status == "SUSPENDED"
    assert aggregate_only_precommit(aggregate) != "ALLOW"


def test_h10_002_fresh_aggregate_must_not_override_registry_revocation():
    aggregate = AggregateStanding(sequence=102, age_seconds=1, product_authorised=True)
    registry = ProductRegistryStanding(sequence=45, status="REVOKED")
    assert registry.status == "REVOKED"
    assert aggregate_only_precommit(aggregate) != "ALLOW"


def test_h10_003_unknown_authoritative_dependency_must_not_fail_open():
    aggregate = AggregateStanding(sequence=103, age_seconds=0, product_authorised=True)
    registry = ProductRegistryStanding(sequence=46, status="UNKNOWN")
    assert registry.status == "UNKNOWN"
    assert aggregate_only_precommit(aggregate) != "ALLOW"


def test_h10_004_newer_aggregate_sequence_does_not_prove_dependency_convergence():
    aggregate = AggregateStanding(sequence=999, age_seconds=0, product_authorised=True)
    registry = ProductRegistryStanding(sequence=47, status="REVOKED")
    assert aggregate.sequence > registry.sequence
    assert aggregate_only_precommit(aggregate) != "ALLOW"
