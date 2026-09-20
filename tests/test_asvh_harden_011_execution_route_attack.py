"""ASVH HARDEN-011 — execution route closure verification.

The first RED is preserved in docs/ASVH-HARDEN-011-FIRST-FAILURE.md.
These tests exercise a structurally guarded represented EPR sink: the sink itself
requires a gateway-issued single-use capability bound to the exact attempt and
payload. Direct/alternate writers therefore encounter the same boundary.
"""
from dataclasses import dataclass, field
import hashlib

from asvh.authority_convergence import (
    ConsequenceBind, PolicyPositionVerifier, TrustPolicyPosition,
    bind_from_position, final_bind_and_execute,
)


def _payload_digest(payload: str) -> str:
    return hashlib.sha256(payload.encode()).hexdigest()


@dataclass
class ProtectedSink:
    commits: list = field(default_factory=list)
    _issued: dict = field(default_factory=dict)
    _consumed: set = field(default_factory=set)

    def _issue(self, bind: ConsequenceBind, attempt_id: str, payload: str) -> str:
        if not bind.complete() or bind.attempt_id != attempt_id:
            raise ValueError("BIND_ATTEMPT_MISMATCH")
        token = hashlib.sha256(
            (bind.digest() + "|" + attempt_id + "|" + _payload_digest(payload)).encode()
        ).hexdigest()
        self._issued[token] = (bind.digest(), attempt_id, _payload_digest(payload))
        return token

    def commit(self, attempt_id: str, payload: str, *, capability: str | None = None) -> str:
        if not capability or capability in self._consumed:
            return "BLOCKED"
        expected = self._issued.get(capability)
        actual = (expected[0], attempt_id, _payload_digest(payload)) if expected else None
        if expected is None or actual != expected:
            return "BLOCKED"
        self._consumed.add(capability)
        self.commits.append((attempt_id, payload))
        return "COMMITTED"


def position(attempt_id="attempt-A"):
    return TrustPolicyPosition(7,"policy-d7","ACTIVE","policy-authority",0,11,
                               "proof","commit-context",attempt_id)


def verifier(attempt_id="attempt-A"):
    return PolicyPositionVerifier("policy-authority","commit-context",5,
                                  lambda _: True,attempt_id)


def valid_bind(attempt_id="attempt-A"):
    return bind_from_position(position(attempt_id))


def gateway_commit(sink, bind, attempt_id="attempt-A", payload="clinical-note",
                   read_policy_position=None, policy_position_verifier=None):
    read_policy_position = read_policy_position or (lambda: position(attempt_id))
    policy_position_verifier = policy_position_verifier or verifier(attempt_id)

    def execute(verified_bind):
        capability = sink._issue(verified_bind, attempt_id, payload)
        return sink.commit(attempt_id, payload, capability=capability)

    return final_bind_and_execute(
        expected_bind=bind,
        read_policy_position=read_policy_position,
        policy_position_verifier=policy_position_verifier,
        execute=execute,
    )


def test_h11_001_direct_protected_commit_must_not_bypass_gateway():
    sink=ProtectedSink()
    assert sink.commit("attempt-A","clinical-note") != "COMMITTED"
    assert sink.commits == []


def test_h11_002_downstream_writer_must_not_ignore_valid_bind():
    sink=ProtectedSink(); bind=valid_bind()
    result=final_bind_and_execute(expected_bind=bind,read_policy_position=lambda:position(),
        policy_position_verifier=verifier(),
        execute=lambda ignored:sink.commit("attempt-A","clinical-note"))
    assert result != "COMMITTED" and sink.commits == []


def test_h11_003_missing_bind_must_not_reach_protected_sink():
    sink=ProtectedSink()
    assert sink.commit("attempt-A","clinical-note") != "COMMITTED"


def test_h11_004_incomplete_bind_must_not_be_usable_as_commit_authority():
    sink=ProtectedSink(); incomplete=ConsequenceBind(7,"policy-d7",11,"commit-context")
    assert incomplete.complete() is False
    assert sink.commit("attempt-A","clinical-note") != "COMMITTED"


def test_h11_005_bind_for_attempt_a_must_not_authorise_attempt_b():
    sink=ProtectedSink(); bind_a=valid_bind("attempt-A")
    # Even if the verified callback tries to form B, the capability issuer refuses.
    result=final_bind_and_execute(expected_bind=bind_a,
        read_policy_position=lambda:position("attempt-A"),
        policy_position_verifier=verifier("attempt-A"),
        execute=lambda verified: _attempt_substitution(sink, verified))
    assert result != "COMMITTED" and sink.commits == []


def _attempt_substitution(sink, verified):
    try:
        cap=sink._issue(verified,"attempt-B","clinical-note")
    except ValueError:
        return "BLOCKED"
    return sink.commit("attempt-B","clinical-note",capability=cap)


def test_h11_006_successfully_used_capability_must_not_be_replayable():
    sink=ProtectedSink(); bind=valid_bind()
    cap=sink._issue(bind,"attempt-A","clinical-note")
    first=sink.commit("attempt-A","clinical-note",capability=cap)
    second=sink.commit("attempt-A","clinical-note",capability=cap)
    assert first=="COMMITTED" and second!="COMMITTED" and len(sink.commits)==1


def test_h11_007_gateway_exception_must_not_leave_direct_commit_route():
    sink=ProtectedSink()
    def unavailable(): raise RuntimeError("authority gateway unavailable")
    result=gateway_commit(sink,valid_bind(),read_policy_position=unavailable)
    assert result != "COMMITTED"
    assert sink.commit("attempt-A","clinical-note") != "COMMITTED"
    assert sink.commits == []


def test_h11_008_alternate_writer_must_share_same_enforcement_boundary():
    sink=ProtectedSink()
    # An alternate adapter has no separate direct-commit primitive; it meets the same sink.
    assert sink.commit("attempt-A","clinical-note") != "COMMITTED"
    assert sink.commits == []


def test_h11_009_happy_path_exact_bind_forms_one_represented_commit():
    sink=ProtectedSink()
    assert gateway_commit(sink,valid_bind()) == "COMMITTED"
    assert sink.commits == [("attempt-A","clinical-note")]


def test_h11_010_payload_substitution_after_capability_issue_is_blocked():
    sink=ProtectedSink(); bind=valid_bind()
    cap=sink._issue(bind,"attempt-A","clinical-note")
    assert sink.commit("attempt-A","altered-note",capability=cap) != "COMMITTED"
    assert sink.commits == []
