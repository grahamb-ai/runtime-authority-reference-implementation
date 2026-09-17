"""Focused hostile tests for HARDEN-010 execution-attempt binding.

These tests isolate HC-H10-FR-042. Presence of a non-empty attempt identity is not
sufficient: the verifier must itself be configured with the expected attempt and
must require exact equality.
"""
from asvh.authority_convergence import TrustPolicyPosition, PolicyPositionVerifier


def position(attempt_id="attacker-attempt"):
    return TrustPolicyPosition(
        8,
        "d8",
        "ACTIVE",
        "policy-authority",
        0,
        20,
        "proof",
        "c",
        attempt_id,
    )


def test_h10_hr57_missing_expected_attempt_must_fail_closed():
    verifier = PolicyPositionVerifier(
        "policy-authority",
        "c",
        5,
        lambda _: True,
    )
    assert verifier.verify(position()) is False


def test_h10_hr58_wrong_nonempty_attempt_must_be_rejected():
    verifier = PolicyPositionVerifier(
        "policy-authority",
        "c",
        5,
        lambda _: True,
        "attempt-1",
    )
    assert verifier.verify(position("attacker-attempt")) is False


def test_h10_hr59_exact_expected_attempt_may_pass_attempt_check():
    verifier = PolicyPositionVerifier(
        "policy-authority",
        "c",
        5,
        lambda _: True,
        "attempt-1",
    )
    assert verifier.verify(position("attempt-1")) is True
