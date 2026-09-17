"""HARDEN-010 authority dependency convergence reference mechanism."""
from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Callable


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
class DependencyBasis:
    dependencies: tuple[AuthorityDependency, ...]


def evaluate_dependency(dep: AuthorityDependency, max_age_seconds: int = 30) -> ConvergenceResult:
    if dep.revision < 0 or dep.age_seconds < 0 or dep.age_seconds > max_age_seconds:
        return ConvergenceResult.INDETERMINATE
    status = dep.status.upper()
    if status in PROHIBITIVE:
        return ConvergenceResult.PREVENTED
    if status in INDETERMINATE or status not in POSITIVE:
        return ConvergenceResult.INDETERMINATE
    return ConvergenceResult.ACTIVE


def converge(basis: DependencyBasis, max_age_seconds: int = 30) -> ConvergenceResult:
    required = [d for d in basis.dependencies if d.required]
    if not required:
        return ConvergenceResult.INDETERMINATE
    seen = set()
    outcome = ConvergenceResult.ACTIVE
    for dep in required:
        key = (dep.source_id, dep.subject_id)
        if key in seen:
            return ConvergenceResult.INDETERMINATE
        seen.add(key)
        result = evaluate_dependency(dep, max_age_seconds)
        if result == ConvergenceResult.PREVENTED:
            return result
        if result == ConvergenceResult.INDETERMINATE:
            outcome = result
    return outcome


def consequence_time_converge(read_current: Callable[[], DependencyBasis], max_age_seconds: int = 30) -> ConvergenceResult:
    """Re-read authoritative dependencies at the consequence boundary."""
    return converge(read_current(), max_age_seconds)
