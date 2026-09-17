"""ASVH HARDEN-010 — convergence-to-consequence TOCTOU attacks.

Frozen before remediation.

A convergence check is not sufficient if authority can change after that check
and before consequence formation. These cases model the race explicitly.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class RegistryState:
    sequence: int
    status: str


class MutableRegistry:
    def __init__(self, state: RegistryState):
        self.state = state

    def read(self) -> RegistryState:
        return self.state

    def advance(self, status: str):
        self.state = RegistryState(self.state.sequence + 1, status)


def naive_check_then_commit(registry: MutableRegistry, mutate_before_commit=None) -> str:
    checked = registry.read()
    if checked.status != "AUTHORISED":
        return "PREVENTED"
    if mutate_before_commit:
        mutate_before_commit()
    # Deliberate failure hypothesis: no authoritative re-bind/recheck here.
    return "COMMITTED"


def test_h10_009_revocation_between_convergence_and_commit_must_prevent_consequence():
    registry = MutableRegistry(RegistryState(60, "AUTHORISED"))
    result = naive_check_then_commit(registry, lambda: registry.advance("REVOKED"))
    assert registry.read().status == "REVOKED"
    assert result != "COMMITTED"


def test_h10_010_suspension_between_convergence_and_commit_must_prevent_consequence():
    registry = MutableRegistry(RegistryState(61, "AUTHORISED"))
    result = naive_check_then_commit(registry, lambda: registry.advance("SUSPENDED"))
    assert registry.read().status == "SUSPENDED"
    assert result != "COMMITTED"


def test_h10_011_unknown_between_convergence_and_commit_must_not_fail_open():
    registry = MutableRegistry(RegistryState(62, "AUTHORISED"))
    result = naive_check_then_commit(registry, lambda: registry.advance("UNKNOWN"))
    assert registry.read().status == "UNKNOWN"
    assert result != "COMMITTED"
