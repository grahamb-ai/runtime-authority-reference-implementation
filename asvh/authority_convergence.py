"""HARDEN-010 authority dependency convergence reference mechanism."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Mapping


class ConvergenceResult(str, Enum):
    ACTIVE = "ACTIVE"
    PREVENTED = "PREVENTED"
    INDETERMINATE = "INDETERMINATE"


POSITIVE = {"AUTHORISED", "VALID", "CLEAR", "ACTIVE"}
PROHIBITIVE = {"REVOKED", "SUSPENDED", "WITHDRAWN", "SUPERSEDED", "EXPIRED", "INVALID"}
INDETERMINATE = {"UNKNOWN", "UNAVAILABLE", "CONFLICT", "INDETERMINATE"}


@dataclass(frozen=True)
class AuthorityDependency:
    source_id: str
    subject_id: str
    revision: int
    status: str
    age_seconds: int
    required: bool = True


@dataclass(frozen=True)
class DependencyRequirement:
    subject_id: str
    authoritative_source_id: str
    required: bool = True


@dataclass(frozen=True)
class DependencyBasis:
    dependencies: tuple[AuthorityDependency, ...]


@dataclass
class AuthorityConvergenceState:
    """Reference high-watermark state; production durability is not claimed."""
    high_watermarks: dict[tuple[str, str], int] = field(default_factory=dict)

    def observe(self, dep: AuthorityDependency) -> ConvergenceResult:
        key = (dep.source_id, dep.subject_id)
        previous = self.high_watermarks.get(key)
        if previous is not None and dep.revision < previous:
            return ConvergenceResult.PREVENTED
        if previous is None or dep.revision > previous:
            self.high_watermarks[key] = dep.revision
        return ConvergenceResult.ACTIVE


def evaluate_dependency(dep: AuthorityDependency, max_age_seconds: int = 30) -> ConvergenceResult:
    if dep.revision < 0 or dep.age_seconds < 0 or dep.age_seconds > max_age_seconds:
        return ConvergenceResult.INDETERMINATE
    status = dep.status.upper()
    if status in PROHIBITIVE:
        return ConvergenceResult.PREVENTED
    if status in INDETERMINATE or status not in POSITIVE:
        return ConvergenceResult.INDETERMINATE
    return ConvergenceResult.ACTIVE


def converge(
    basis: DependencyBasis,
    max_age_seconds: int = 30,
    *,
    requirements: tuple[DependencyRequirement, ...] | None = None,
    state: AuthorityConvergenceState | None = None,
) -> ConvergenceResult:
    required_deps = [d for d in basis.dependencies if d.required]
    if not required_deps:
        return ConvergenceResult.INDETERMINATE

    if requirements is not None:
        expected = {(r.authoritative_source_id, r.subject_id) for r in requirements if r.required}
        actual = {(d.source_id, d.subject_id) for d in required_deps}
        # Missing authority, unexpected substitution, or extra required authority is unresolved.
        if actual != expected:
            return ConvergenceResult.INDETERMINATE

    seen_identity: set[tuple[str, str]] = set()
    seen_subject_revision: dict[tuple[str, int], str] = {}
    outcome = ConvergenceResult.ACTIVE

    for dep in required_deps:
        identity = (dep.source_id, dep.subject_id)
        if identity in seen_identity:
            return ConvergenceResult.INDETERMINATE
        seen_identity.add(identity)

        conflict_key = (dep.subject_id, dep.revision)
        prior_status = seen_subject_revision.get(conflict_key)
        if prior_status is not None and prior_status != dep.status.upper():
            return ConvergenceResult.INDETERMINATE
        seen_subject_revision[conflict_key] = dep.status.upper()

        if state is not None:
            monotonic = state.observe(dep)
            if monotonic != ConvergenceResult.ACTIVE:
                return monotonic

        result = evaluate_dependency(dep, max_age_seconds)
        if result == ConvergenceResult.PREVENTED:
            return result
        if result == ConvergenceResult.INDETERMINATE:
            outcome = result
    return outcome


def consequence_time_converge(
    read_current: Callable[[], DependencyBasis],
    max_age_seconds: int = 30,
    *,
    requirements: tuple[DependencyRequirement, ...] | None = None,
    state: AuthorityConvergenceState | None = None,
) -> ConvergenceResult:
    """Re-read authoritative dependencies at the consequence boundary."""
    return converge(read_current(), max_age_seconds, requirements=requirements, state=state)
