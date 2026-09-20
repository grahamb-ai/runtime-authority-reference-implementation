"""ASVH-AIRP-002 — worked evidence case.

Pre-beta exercise against ORCHA's publicly described AiRP methodology.
This is not an official AiRP assessment.

Property: an earlier legitimate documentation path must not be enough to form the
represented clinical-record consequence after a relevant authority dependency
changes before the consequence boundary.
"""
from asvh.authority_convergence import (
    AuthorityDependency, DependencyBasis, ConvergenceResult,
    consequence_time_converge,
)


def _basis(consent_status: str, revision: int) -> DependencyBasis:
    return DependencyBasis((
        AuthorityDependency(
            source_id="consent-authority",
            subject_id="synthetic-patient/encounter-001",
            revision=revision,
            status=consent_status,
            age_seconds=0,
            required=True,
        ),
    ))


def test_airp_002_state_change_blocks_represented_clinical_record_commit():
    # T0: the workflow is legitimately initiated while the relevant condition holds.
    earlier = _basis("VALID", 1)

    # T1: immediately before represented consequence formation, the authoritative
    # condition has changed. The earlier workflow state still exists, but is not
    # treated as present standing.
    current = _basis("WITHDRAWN", 2)

    earlier_result, _ = consequence_time_converge(lambda: earlier)
    runtime_result, runtime_bind = consequence_time_converge(lambda: current)

    represented_epr_commits = []
    if runtime_result == ConvergenceResult.ACTIVE:
        represented_epr_commits.append("synthetic-note")

    assert earlier_result == ConvergenceResult.ACTIVE
    assert runtime_result == ConvergenceResult.PREVENTED
    assert runtime_bind is None
    assert represented_epr_commits == []


def test_airp_002_without_runtime_revalidation_has_no_evidence_of_present_standing():
    # Comparator only: an earlier VALID observation can describe historical state,
    # but by itself contains no evidence that the condition still holds at T1.
    earlier = _basis("VALID", 1)
    current = _basis("WITHDRAWN", 2)

    earlier_result, _ = consequence_time_converge(lambda: earlier)
    current_result, _ = consequence_time_converge(lambda: current)

    assert earlier_result == ConvergenceResult.ACTIVE
    assert current_result == ConvergenceResult.PREVENTED
    # Deliberately no assertion that a real EPR would commit without FlowSignal.
    # That external consequence remains NOT DEMONSTRATED.
