"""Failure-first attacks on the HARDEN-010 recovery trust root."""
from asvh.authority_convergence import (
    AuthorityConvergenceState, RecoveredAuthorityRecord, RecoveryEvidence,
    RecoveryVerifier, recovery_records_digest,
)

RECORDS=(RecoveredAuthorityRecord("registry","product-x",400,"AUTHORISED"),)
DIGEST=recovery_records_digest(RECORDS)

def evidence(verifier="trusted", context="recovery-42", digest=DIGEST, attestation="opaque-proof"):
    return RecoveryEvidence(True,True,True,frozenset({("registry","product-x")}),verifier,digest,context,attestation)

def verifier(ids=frozenset({"trusted"}),context="recovery-42",fn=lambda _: True):
    return RecoveryVerifier(ids,context,fn)

def test_h10_hr23_caller_supplied_always_true_verifier_must_not_create_trust_root():
    state=AuthorityConvergenceState.recover(RECORDS,evidence(),verifier(fn=lambda _: True))
    assert state.recovery_trusted is False

def test_h10_hr24_attacker_selected_trusted_verifier_set_must_not_create_trust():
    ev=evidence(verifier="evil")
    state=AuthorityConvergenceState.recover(RECORDS,ev,verifier(ids=frozenset({"evil"})))
    assert state.recovery_trusted is False

def test_h10_hr25_attacker_selected_context_must_not_validate_own_replay_domain():
    ev=evidence(context="attacker-context")
    state=AuthorityConvergenceState.recover(RECORDS,ev,verifier(context="attacker-context"))
    assert state.recovery_trusted is False

def test_h10_hr26_digest_is_order_canonical_for_equivalent_record_set():
    records=(RecoveredAuthorityRecord("b","2",1,"VALID"),RecoveredAuthorityRecord("a","1",2,"AUTHORISED"))
    assert recovery_records_digest(records)==recovery_records_digest(tuple(reversed(records)))

def test_h10_hr27_digest_must_change_when_semantic_status_changes():
    changed=(RecoveredAuthorityRecord("registry","product-x",400,"REVOKED"),)
    assert recovery_records_digest(RECORDS)!=recovery_records_digest(changed)

def test_h10_hr28_duplicate_record_injection_must_not_be_attestable_as_distinct_valid_history():
    duplicated=RECORDS+RECORDS
    ev=evidence(digest=recovery_records_digest(duplicated))
    state=AuthorityConvergenceState.recover(duplicated,ev,verifier())
    assert state.recovery_trusted is False

def test_h10_hr29_valid_attestation_from_prior_recovery_epoch_must_not_replay():
    ev=evidence(context="recovery-41")
    state=AuthorityConvergenceState.recover(RECORDS,ev,verifier(context="recovery-42"))
    assert state.recovery_trusted is False
