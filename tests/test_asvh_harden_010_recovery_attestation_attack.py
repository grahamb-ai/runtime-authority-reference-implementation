"""Failure-first attacks on RecoveryEvidence attestation semantics."""
from asvh.authority_convergence import (
    AuthorityConvergenceState, RecoveredAuthorityRecord, RecoveryEvidence
)


def rr(source="registry", subject="product-x", revision=300, status="AUTHORISED"):
    return RecoveredAuthorityRecord(source, subject, revision, status)


def ev(covered=frozenset({("registry", "product-x")})):
    return RecoveryEvidence(True, True, True, covered)


def test_h10_hr17_self_asserted_verification_flags_are_not_proof():
    # Hostile caller simply sets every verification flag True.
    state = AuthorityConvergenceState.recover((rr(),), ev())
    assert state.recovery_trusted is False


def test_h10_hr18_attestation_for_one_record_set_cannot_be_replayed_for_mutated_records():
    evidence = ev()
    # Evidence conceptually issued for rev300, but records are mutated to rev999 before recovery.
    state = AuthorityConvergenceState.recover((rr(revision=999),), evidence)
    assert state.recovery_trusted is False


def test_h10_hr19_attestation_must_identify_verifier():
    evidence = ev()
    assert hasattr(evidence, "verifier_id") and bool(evidence.verifier_id)


def test_h10_hr20_attestation_must_bind_exact_record_digest():
    evidence = ev()
    assert hasattr(evidence, "records_digest") and bool(evidence.records_digest)


def test_h10_hr21_attestation_must_bind_recovery_context_or_epoch():
    evidence = ev()
    assert hasattr(evidence, "recovery_context") and bool(evidence.recovery_context)


def test_h10_hr22_coverage_identity_alone_cannot_authenticate_source():
    # Exact strings can be forged; coverage matching alone must not establish trust.
    forged = rr(source="registry", subject="product-x", revision=999999)
    state = AuthorityConvergenceState.recover((forged,), ev())
    assert state.recovery_trusted is False
