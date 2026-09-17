"""Failure-first attacks on consequence-time trust-policy position evidence."""
from asvh.authority_convergence import TrustPolicyPosition


def pos(rev=10,digest="digest-a",standing="ACTIVE"):
    return TrustPolicyPosition(rev,digest,standing)


def test_h10_hr37_policy_position_identifies_authoritative_source():
    assert hasattr(pos(),"source_id") and bool(pos().source_id)


def test_h10_hr38_policy_position_carries_freshness_evidence():
    assert hasattr(pos(),"age_seconds")


def test_h10_hr39_negative_policy_position_age_is_rejected():
    p=pos()
    assert hasattr(p,"age_seconds") and p.age_seconds >= 0


def test_h10_hr40_same_revision_different_digest_is_explicit_equivocation_not_simple_staleness():
    a=pos(10,"digest-a"); b=pos(10,"digest-b")
    assert hasattr(a,"authority_epoch") and a.authority_epoch == b.authority_epoch


def test_h10_hr41_forged_higher_revision_is_not_self_authenticating():
    p=pos(999999,"attacker-digest","ACTIVE")
    assert hasattr(p,"attestation") and bool(p.attestation)


def test_h10_hr42_unavailable_policy_authority_is_not_representable_as_active_position():
    p=pos(10,"digest-a","UNAVAILABLE")
    assert p.standing != "UNAVAILABLE"


def test_h10_hr43_policy_position_source_substitution_is_detectable():
    p=pos()
    assert hasattr(p,"source_id") and p.source_id == "policy-authority"


def test_h10_hr44_policy_position_must_bind_observation_context():
    p=pos()
    assert hasattr(p,"observation_context") and bool(p.observation_context)
