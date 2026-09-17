"""ASVH HARDEN-011 — failure-first execution route closure attacks.

Frozen before H11 remediation. These attacks intentionally expose the structural
residual carried forward from HARDEN-010 rather than pretending the arbitrary
callback boundary is non-bypassable.
"""
from dataclasses import dataclass

from asvh.authority_convergence import (
    ConsequenceBind,
    PolicyPositionVerifier,
    TrustPolicyPosition,
    bind_from_position,
    final_bind_and_execute,
)


@dataclass
class ProtectedSink:
    commits: list

    def direct_commit(self, attempt_id: str, payload: str) -> str:
        # Deliberate pre-remediation model: the sink is independently callable.
        self.commits.append((attempt_id, payload))
        return "COMMITTED"


def position(attempt_id="attempt-A"):
    return TrustPolicyPosition(
        7,
        "policy-d7",
        "ACTIVE",
        "policy-authority",
        0,
        11,
        "proof",
        "commit-context",
        attempt_id,
    )


def verifier(attempt_id="attempt-A"):
    return PolicyPositionVerifier(
        "policy-authority",
        "commit-context",
        5,
        lambda _: True,
        attempt_id,
    )


def valid_bind(attempt_id="attempt-A"):
    return bind_from_position(position(attempt_id))


def test_h11_001_direct_protected_commit_must_not_bypass_gateway():
    sink = ProtectedSink([])
    result = sink.direct_commit("attempt-A", "clinical-note")
    assert result != "COMMITTED"
    assert sink.commits == []


def test_h11_002_downstream_writer_must_not_ignore_valid_bind():
    sink = ProtectedSink([])
    bind = valid_bind()
    result = final_bind_and_execute(
        expected_bind=bind,
        read_policy_position=lambda: position(),
        policy_position_verifier=verifier(),
        execute=lambda ignored: sink.direct_commit("attempt-A", "clinical-note"),
    )
    assert result != "COMMITTED"
    assert sink.commits == []


def test_h11_003_missing_bind_must_not_reach_protected_sink():
    sink = ProtectedSink([])
    # Direct sink invocation models an alternate adapter/writer path.
    result = sink.direct_commit("attempt-A", "clinical-note")
    assert result != "COMMITTED"
    assert sink.commits == []


def test_h11_004_incomplete_bind_must_not_be_usable_as_commit_authority():
    sink = ProtectedSink([])
    incomplete = ConsequenceBind(7, "policy-d7", 11, "commit-context")
    assert incomplete.complete() is False
    result = sink.direct_commit("attempt-A", "clinical-note")
    assert result != "COMMITTED"
    assert sink.commits == []


def test_h11_005_bind_for_attempt_a_must_not_authorise_attempt_b():
    sink = ProtectedSink([])
    bind_a = valid_bind("attempt-A")
    # The reference callback can ignore bind_a and form attempt-B consequence.
    result = final_bind_and_execute(
        expected_bind=bind_a,
        read_policy_position=lambda: position("attempt-A"),
        policy_position_verifier=verifier("attempt-A"),
        execute=lambda ignored: sink.direct_commit("attempt-B", "clinical-note"),
    )
    assert result != "COMMITTED"
    assert sink.commits == []


def test_h11_006_successfully_used_bind_must_not_be_replayable():
    sink = ProtectedSink([])
    bind = valid_bind()

    def execute(_):
        return sink.direct_commit("attempt-A", "clinical-note")

    first = final_bind_and_execute(
        expected_bind=bind,
        read_policy_position=lambda: position(),
        policy_position_verifier=verifier(),
        execute=execute,
    )
    second = final_bind_and_execute(
        expected_bind=bind,
        read_policy_position=lambda: position(),
        policy_position_verifier=verifier(),
        execute=execute,
    )
    assert not (first == "COMMITTED" and second == "COMMITTED")
    assert len(sink.commits) <= 1


def test_h11_007_gateway_exception_must_not_leave_direct_commit_route():
    sink = ProtectedSink([])

    def unavailable():
        raise RuntimeError("authority gateway unavailable")

    # The gateway itself fails closed, but an independently callable sink still
    # exposes a route around it. H11 requires structural closure of that route.
    final_bind_and_execute(
        expected_bind=valid_bind(),
        read_policy_position=unavailable,
        policy_position_verifier=verifier(),
        execute=lambda _: sink.direct_commit("attempt-A", "clinical-note"),
    )
    bypass = sink.direct_commit("attempt-A", "clinical-note")
    assert bypass != "COMMITTED"
    assert sink.commits == []


def test_h11_008_alternate_writer_must_share_same_enforcement_boundary():
    primary = ProtectedSink([])
    alternate = ProtectedSink([])
    # Even if a primary route were guarded, the alternate remains callable.
    result = alternate.direct_commit("attempt-A", "clinical-note")
    assert result != "COMMITTED"
    assert primary.commits == [] and alternate.commits == []
