"""Failure-first attacks on recovery trust-policy lifecycle and present standing."""
from asvh.authority_convergence import (
    AuthorityConvergenceState, RecoveredAuthorityRecord, RecoveryEvidence,
    RecoveryVerifier, RecoveryTrustPolicy, recovery_records_digest,
)

PRODUCT=("registry","product-x")
WORKFLOW=("workflow-authority","workflow-y")
RECORDS=(RecoveredAuthorityRecord(*PRODUCT,500,"AUTHORISED"),)

def evidence(records=RECORDS, verifier_id="verifier-a", context="epoch-50"):
    return RecoveryEvidence(True,True,True,frozenset((r.source_id,r.subject_id) for r in records),verifier_id,recovery_records_digest(records),context,"proof")

def policy(records=RECORDS, verifier_id="verifier-a", context="epoch-50"):
    return RecoveryTrustPolicy(RecoveryVerifier(frozenset({verifier_id}),context,lambda _: True),frozenset((r.source_id,r.subject_id) for r in records))

def test_h10_hr30_policy_has_monotonic_version_or_epoch():
    p=policy()
    assert hasattr(p,"policy_revision") and isinstance(p.policy_revision,int)

def test_h10_hr31_old_once_valid_policy_cannot_be_replayed_after_newer_policy_exists():
    old=policy(context="epoch-49")
    ev=evidence(context="epoch-49")
    state=AuthorityConvergenceState.recover(RECORDS,ev,trust_policy=old)
    assert state.recovery_trusted is False

def test_h10_hr32_withdrawn_verifier_cannot_remain_valid_via_old_policy_object():
    old=policy(verifier_id="verifier-a")
    ev=evidence(verifier_id="verifier-a")
    state=AuthorityConvergenceState.recover(RECORDS,ev,trust_policy=old)
    assert state.recovery_trusted is False

def test_h10_hr33_authority_set_downgrade_must_not_silently_drop_required_dependency():
    # Older policy requires only product; current policy is assumed to require product + workflow.
    old=policy(records=RECORDS)
    state=AuthorityConvergenceState.recover(RECORDS,evidence(),trust_policy=old)
    assert state.recovery_trusted is False

def test_h10_hr34_policy_must_expose_current_standing_or_revocation_state():
    p=policy()
    assert hasattr(p,"standing")

def test_h10_hr35_policy_must_be_bound_to_attestation_evidence():
    ev=evidence()
    assert hasattr(ev,"trust_policy_digest") and bool(ev.trust_policy_digest)

def test_h10_hr36_recovery_trust_must_not_outlive_policy_change_before_consequence():
    state=AuthorityConvergenceState.recover(RECORDS,evidence(),trust_policy=policy())
    # A successful recovery under policy A must not create durable authority if policy standing changes.
    assert state.recovery_trusted is False
