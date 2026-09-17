"""Failure-first hostile attacks against HARDEN-010 recovery records."""
from asvh.authority_convergence import (
    AuthorityDependency, DependencyBasis, DependencyRequirement,
    AuthorityConvergenceState, RecoveredAuthorityRecord,
    ConvergenceResult, converge,
)


def rr(source, subject, revision, status):
    return RecoveredAuthorityRecord(source, subject, revision, status)


def dep(source, subject, revision, status="AUTHORISED"):
    return AuthorityDependency(source, subject, revision, status, 0)


PRODUCT = DependencyRequirement("product-x", "registry")
WORKFLOW = DependencyRequirement("workflow-y", "workflow-authority")


def test_h10_hr11_empty_recovery_record_set_must_not_be_trusted():
    state = AuthorityConvergenceState.recover(())
    assert state.recovery_trusted is False


def test_h10_hr12_truncated_recovery_missing_required_dependency_must_not_activate():
    state = AuthorityConvergenceState.recover((rr("registry", "product-x", 200, "AUTHORISED"),))
    basis = DependencyBasis((dep("registry", "product-x", 201), dep("workflow-authority", "workflow-y", 91, "VALID")))
    assert converge(basis, requirements=(PRODUCT, WORKFLOW), state=state) != ConvergenceResult.ACTIVE


def test_h10_hr13_recovery_with_conflicting_same_revision_must_be_untrusted():
    state = AuthorityConvergenceState.recover((
        rr("registry", "product-x", 210, "AUTHORISED"),
        rr("registry", "product-x", 210, "REVOKED"),
    ))
    assert state.recovery_trusted is False


def test_h10_hr14_recovery_with_negative_revision_must_be_untrusted():
    state = AuthorityConvergenceState.recover((rr("registry", "product-x", -1, "AUTHORISED"),))
    assert state.recovery_trusted is False


def test_h10_hr15_forged_higher_positive_revision_must_not_be_self_authenticating():
    state = AuthorityConvergenceState.recover((rr("registry", "product-x", 999999, "AUTHORISED"),))
    assert state.recovery_trusted is False


def test_h10_hr16_recovery_omitting_newer_revocation_must_not_allow_older_positive_lineage():
    # Recovery presents only revision 220 AUTHORISED, while the real durable history may have contained 221 REVOKED.
    # Without integrity/completeness evidence, the record set must not be treated as authoritative recovery.
    state = AuthorityConvergenceState.recover((rr("registry", "product-x", 220, "AUTHORISED"),))
    assert state.recovery_trusted is False
