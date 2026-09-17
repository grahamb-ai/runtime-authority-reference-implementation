"""HARDEN-010 isolated attack on the executor enforcement boundary.

This test deliberately uses a complete canonical consequence bind so rejection cannot
be attributed to the incomplete historical HR52 fixture. It asks only whether the
reference callback boundary can force the executor to enforce the bind it receives.
"""
from asvh.authority_convergence import (
    TrustPolicyPosition,
    PolicyPositionVerifier,
    bind_from_position,
    final_bind_and_execute,
)


def test_h10_hr56_valid_bind_must_not_be_ignorable_by_executor():
    position = TrustPolicyPosition(
        8,
        "d8",
        "ACTIVE",
        "policy-authority",
        0,
        20,
        "proof",
        "c",
        "attempt-1",
    )
    verifier = PolicyPositionVerifier(
        "policy-authority",
        "c",
        5,
        lambda _: True,
        "attempt-1",
    )
    binding = bind_from_position(position)

    def executor(_ignored_bind):
        return "COMMITTED"

    result = final_bind_and_execute(
        expected_bind=binding,
        read_policy_position=lambda: position,
        policy_position_verifier=verifier,
        execute=executor,
    )

    assert result != "COMMITTED"
