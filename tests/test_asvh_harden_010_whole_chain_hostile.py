"""HARDEN-010 whole-chain hostile verification.

Exercises the remediated reference path across authoritative dependency convergence,
current policy standing, exact execution-attempt binding, consequence binding and
final consequence-time reread.

This suite deliberately stops at the Python callback boundary. It does not claim
production executor/EPR non-bypassability; HC-H10-FR-041 / HR56 remains open.
"""
from asvh.authority_convergence import (
    AuthorityDependency,
    AuthorityConvergenceState,
    ConvergenceResult,
    DependencyBasis,
    DependencyRequirement,
    PolicyPositionVerifier,
    TrustPolicyPosition,
    consequence_time_converge,
    final_bind_and_execute,
)

REQ = (DependencyRequirement("product-x", "registry"),)
ATTEMPT = "attempt-closure-1"
CONTEXT = "commit-closure-1"


def dependency(revision=100, status="AUTHORISED", age_seconds=0, source="registry"):
    return AuthorityDependency(source, "product-x", revision, status, age_seconds)


def position(
    *,
    policy_revision=7,
    policy_digest="policy-d7",
    standing="ACTIVE",
    source_id="policy-authority",
    age_seconds=0,
    authority_epoch=11,
    attestation="policy-proof",
    observation_context=CONTEXT,
    attempt_id=ATTEMPT,
):
    return TrustPolicyPosition(
        policy_revision,
        policy_digest,
        standing,
        source_id,
        age_seconds,
        authority_epoch,
        attestation,
        observation_context,
        attempt_id,
    )


def verifier(*, attempt_id=ATTEMPT):
    return PolicyPositionVerifier(
        "policy-authority",
        CONTEXT,
        5,
        lambda _: True,
        attempt_id,
    )


def recovered_state():
    # Model a state whose recovery trust was established under the same policy
    # revision/digest now being revalidated at consequence time.
    return AuthorityConvergenceState(
        recovery_trusted=True,
        recovery_policy_revision=7,
        recovery_policy_digest="policy-d7",
    )


def converge_to_bind(*, read_dependency, read_policy=lambda: position(), policy_verifier=None):
    return consequence_time_converge(
        lambda: DependencyBasis((read_dependency(),)),
        requirements=REQ,
        state=recovered_state(),
        read_policy_position=read_policy,
        policy_position_verifier=policy_verifier or verifier(),
    )


def test_h10_hr60_valid_whole_chain_reaches_reference_consequence_callback():
    result, bind = converge_to_bind(read_dependency=lambda: dependency())
    assert result == ConvergenceResult.ACTIVE
    assert bind is not None and bind.complete()
    assert final_bind_and_execute(
        expected_bind=bind,
        read_policy_position=lambda: position(),
        policy_position_verifier=verifier(),
        execute=lambda _: "COMMITTED",
    ) == "COMMITTED"


def test_h10_hr61_dependency_revoked_at_convergence_must_not_create_bind():
    result, bind = converge_to_bind(read_dependency=lambda: dependency(status="REVOKED"))
    assert result == ConvergenceResult.PREVENTED
    assert bind is None


def test_h10_hr62_dependency_unknown_at_convergence_must_not_create_bind():
    result, bind = converge_to_bind(read_dependency=lambda: dependency(status="UNKNOWN"))
    assert result == ConvergenceResult.INDETERMINATE
    assert bind is None


def test_h10_hr63_policy_revoked_before_convergence_must_not_create_bind():
    result, bind = converge_to_bind(
        read_dependency=lambda: dependency(),
        read_policy=lambda: position(standing="REVOKED"),
    )
    assert result == ConvergenceResult.INDETERMINATE
    assert bind is None


def test_h10_hr64_wrong_attempt_before_convergence_must_not_create_bind():
    result, bind = converge_to_bind(
        read_dependency=lambda: dependency(),
        read_policy=lambda: position(attempt_id="other-attempt"),
    )
    assert result == ConvergenceResult.INDETERMINATE
    assert bind is None


def test_h10_hr65_missing_expected_attempt_before_convergence_must_fail_closed():
    result, bind = converge_to_bind(
        read_dependency=lambda: dependency(),
        policy_verifier=verifier(attempt_id=""),
    )
    assert result == ConvergenceResult.INDETERMINATE
    assert bind is None


def test_h10_hr66_policy_revoked_after_bind_before_final_consequence_must_fail_closed():
    result, bind = converge_to_bind(read_dependency=lambda: dependency())
    assert result == ConvergenceResult.ACTIVE and bind is not None
    assert final_bind_and_execute(
        expected_bind=bind,
        read_policy_position=lambda: position(standing="REVOKED"),
        policy_position_verifier=verifier(),
        execute=lambda _: "COMMITTED",
    ) == ConvergenceResult.INDETERMINATE


def test_h10_hr67_policy_digest_change_after_bind_must_fail_closed():
    result, bind = converge_to_bind(read_dependency=lambda: dependency())
    assert result == ConvergenceResult.ACTIVE and bind is not None
    assert final_bind_and_execute(
        expected_bind=bind,
        read_policy_position=lambda: position(policy_digest="policy-d8"),
        policy_position_verifier=verifier(),
        execute=lambda _: "COMMITTED",
    ) == ConvergenceResult.INDETERMINATE


def test_h10_hr68_policy_epoch_change_after_bind_must_fail_closed():
    result, bind = converge_to_bind(read_dependency=lambda: dependency())
    assert result == ConvergenceResult.ACTIVE and bind is not None
    assert final_bind_and_execute(
        expected_bind=bind,
        read_policy_position=lambda: position(authority_epoch=12),
        policy_position_verifier=verifier(),
        execute=lambda _: "COMMITTED",
    ) == ConvergenceResult.INDETERMINATE


def test_h10_hr69_attempt_substitution_after_bind_must_fail_closed():
    result, bind = converge_to_bind(read_dependency=lambda: dependency())
    assert result == ConvergenceResult.ACTIVE and bind is not None
    assert final_bind_and_execute(
        expected_bind=bind,
        read_policy_position=lambda: position(attempt_id="other-attempt"),
        policy_position_verifier=verifier(),
        execute=lambda _: "COMMITTED",
    ) == ConvergenceResult.INDETERMINATE


def test_h10_hr70_policy_source_substitution_after_bind_must_fail_closed():
    result, bind = converge_to_bind(read_dependency=lambda: dependency())
    assert result == ConvergenceResult.ACTIVE and bind is not None
    assert final_bind_and_execute(
        expected_bind=bind,
        read_policy_position=lambda: position(source_id="lookalike-policy-authority"),
        policy_position_verifier=verifier(),
        execute=lambda _: "COMMITTED",
    ) == ConvergenceResult.INDETERMINATE


def test_h10_hr71_policy_attestation_change_after_bind_must_fail_closed():
    result, bind = converge_to_bind(read_dependency=lambda: dependency())
    assert result == ConvergenceResult.ACTIVE and bind is not None
    assert final_bind_and_execute(
        expected_bind=bind,
        read_policy_position=lambda: position(attestation="different-proof"),
        policy_position_verifier=verifier(),
        execute=lambda _: "COMMITTED",
    ) == ConvergenceResult.INDETERMINATE


def test_h10_hr72_policy_reader_failure_at_final_bind_must_fail_closed():
    result, bind = converge_to_bind(read_dependency=lambda: dependency())
    assert result == ConvergenceResult.ACTIVE and bind is not None

    def unavailable():
        raise RuntimeError("policy authority unavailable")

    assert final_bind_and_execute(
        expected_bind=bind,
        read_policy_position=unavailable,
        policy_position_verifier=verifier(),
        execute=lambda _: "COMMITTED",
    ) == ConvergenceResult.INDETERMINATE
