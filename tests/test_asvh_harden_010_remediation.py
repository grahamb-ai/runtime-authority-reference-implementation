from asvh.authority_convergence import (
    AuthorityDependency, DependencyBasis, ConvergenceResult,
    converge, consequence_time_converge,
)


def dep(source, revision, status, age=0, subject="product-x"):
    return AuthorityDependency(source, subject, revision, status, age)


def test_h10_r01_all_required_current_positive_is_active():
    basis = DependencyBasis((dep("registry", 50, "AUTHORISED"), dep("deployment", 77, "VALID")))
    assert converge(basis) == ConvergenceResult.ACTIVE


def test_h10_r02_authoritative_revocation_is_not_outvoted():
    basis = DependencyBasis((dep("registry", 51, "REVOKED"), dep("deployment", 78, "VALID"), dep("aggregate", 1002, "AUTHORISED")))
    assert converge(basis) == ConvergenceResult.PREVENTED


def test_h10_r03_suspension_is_not_outvoted():
    basis = DependencyBasis((dep("registry", 52, "SUSPENDED"), dep("deployment", 79, "VALID"), dep("aggregate", 1003, "AUTHORISED")))
    assert converge(basis) == ConvergenceResult.PREVENTED


def test_h10_r04_unknown_required_dependency_is_indeterminate():
    basis = DependencyBasis((dep("registry", 53, "UNKNOWN"), dep("deployment", 80, "VALID")))
    assert converge(basis) == ConvergenceResult.INDETERMINATE


def test_h10_r05_stale_dependency_is_indeterminate():
    assert converge(DependencyBasis((dep("registry", 54, "AUTHORISED", 31),))) == ConvergenceResult.INDETERMINATE


def test_h10_r06_negative_age_is_indeterminate():
    assert converge(DependencyBasis((dep("registry", 55, "AUTHORISED", -1),))) == ConvergenceResult.INDETERMINATE


def test_h10_r07_duplicate_authority_identity_is_indeterminate():
    basis = DependencyBasis((dep("registry", 56, "AUTHORISED"), dep("registry", 57, "AUTHORISED")))
    assert converge(basis) == ConvergenceResult.INDETERMINATE


def test_h10_r08_no_required_dependencies_fails_closed():
    assert converge(DependencyBasis(())) == ConvergenceResult.INDETERMINATE


def test_h10_r09_consequence_time_revocation_is_seen():
    state = {"status": "AUTHORISED", "revision": 60}
    def read():
        return DependencyBasis((dep("registry", state["revision"], state["status"]),))
    assert consequence_time_converge(read) == ConvergenceResult.ACTIVE
    state.update(status="REVOKED", revision=61)
    assert consequence_time_converge(read) == ConvergenceResult.PREVENTED


def test_h10_r10_consequence_time_unknown_does_not_fail_open():
    state = {"status": "AUTHORISED", "revision": 62}
    def read():
        return DependencyBasis((dep("registry", state["revision"], state["status"]),))
    assert consequence_time_converge(read) == ConvergenceResult.ACTIVE
    state.update(status="UNKNOWN", revision=63)
    assert consequence_time_converge(read) == ConvergenceResult.INDETERMINATE
