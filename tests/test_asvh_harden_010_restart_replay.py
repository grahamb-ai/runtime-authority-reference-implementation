"""Failure-first attacks on HARDEN-010 remediation candidate recovery semantics.

Do not weaken these assertions to obtain green results.
"""
from asvh.authority_convergence import (
    AuthorityDependency, DependencyBasis, DependencyRequirement,
    AuthorityConvergenceState, ConvergenceResult, converge,
)


def d(revision, status="AUTHORISED", source="registry", subject="product-x"):
    return AuthorityDependency(source, subject, revision, status, 0)


REQ = (DependencyRequirement("product-x", "registry"),)


def test_h10_hr06_restart_must_not_erase_revision_floor():
    before_restart = AuthorityConvergenceState()
    assert converge(DependencyBasis((d(100),)), requirements=REQ, state=before_restart) == ConvergenceResult.ACTIVE
    # Hostile restart: volatile state is lost.
    after_restart = AuthorityConvergenceState()
    assert converge(DependencyBasis((d(99),)), requirements=REQ, state=after_restart) != ConvergenceResult.ACTIVE


def test_h10_hr07_missing_recovery_state_must_not_fail_open():
    # A process with no trustworthy recovered watermark must not establish ACTIVE
    # merely from an old positive observation.
    recovered = AuthorityConvergenceState()
    assert converge(DependencyBasis((d(1),)), requirements=REQ, state=recovered) != ConvergenceResult.ACTIVE


def test_h10_hr08_source_alias_after_restart_must_not_satisfy_authority():
    recovered = AuthorityConvergenceState()
    substituted = d(101, source="registry-alias")
    assert converge(DependencyBasis((substituted,)), requirements=REQ, state=recovered) != ConvergenceResult.ACTIVE


def test_h10_hr09_replayed_positive_must_not_override_recovered_revocation():
    recovered = AuthorityConvergenceState()
    assert converge(DependencyBasis((d(110, "REVOKED"),)), requirements=REQ, state=recovered) == ConvergenceResult.PREVENTED
    assert converge(DependencyBasis((d(109, "AUTHORISED"),)), requirements=REQ, state=recovered) != ConvergenceResult.ACTIVE


def test_h10_hr10_recovery_conflict_must_not_become_active():
    recovered = AuthorityConvergenceState()
    assert converge(DependencyBasis((d(120, "AUTHORISED"),)), requirements=REQ, state=recovered) == ConvergenceResult.ACTIVE
    # Same authority revision now claims the opposite standing.
    assert converge(DependencyBasis((d(120, "REVOKED"),)), requirements=REQ, state=recovered) == ConvergenceResult.INDETERMINATE
