from asvh.authority_convergence import (
    AuthorityDependency, DependencyBasis, DependencyRequirement,
    AuthorityConvergenceState, ConvergenceResult, converge,
)


def d(source, subject, revision, status, age=0):
    return AuthorityDependency(source, subject, revision, status, age)


def test_h10_hr01_rollback_revision_is_prevented():
    state = AuthorityConvergenceState()
    requirements = (DependencyRequirement("product-x", "registry"),)
    current = d("registry", "product-x", 100, "AUTHORISED")
    assert converge(DependencyBasis((current,)), requirements=requirements, state=state) == ConvergenceResult.ACTIVE
    replayed = d("registry", "product-x", 99, "AUTHORISED")
    assert converge(DependencyBasis((replayed,)), requirements=requirements, state=state) != ConvergenceResult.ACTIVE


def test_h10_hr02_same_revision_conflicting_status_is_indeterminate():
    requirements = (DependencyRequirement("product-x", "registry-a"), DependencyRequirement("product-x", "registry-b"))
    a = d("registry-a", "product-x", 200, "AUTHORISED")
    b = d("registry-b", "product-x", 200, "REVOKED")
    assert converge(DependencyBasis((a, b)), requirements=requirements) == ConvergenceResult.INDETERMINATE


def test_h10_hr03_source_substitution_is_indeterminate():
    requirements = (DependencyRequirement("product-x", "registry"),)
    substituted = d("registry-lookalike", "product-x", 300, "AUTHORISED")
    assert converge(DependencyBasis((substituted,)), requirements=requirements) != ConvergenceResult.ACTIVE


def test_h10_hr04_missing_declared_authority_is_indeterminate():
    requirements = (DependencyRequirement("product-x", "registry"),)
    assert converge(DependencyBasis((d("deployment", "product-x", 301, "VALID"),)), requirements=requirements) == ConvergenceResult.INDETERMINATE


def test_h10_hr05_extra_required_source_cannot_smuggle_permission():
    requirements = (DependencyRequirement("product-x", "registry"),)
    basis = DependencyBasis((d("registry", "product-x", 302, "AUTHORISED"), d("lookalike", "product-x", 9999, "AUTHORISED")))
    assert converge(basis, requirements=requirements) == ConvergenceResult.INDETERMINATE
