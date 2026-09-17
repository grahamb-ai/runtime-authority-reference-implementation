from asvh.authority_convergence import AuthorityDependency, DependencyBasis, ConvergenceResult, converge


def d(source, subject, revision, status, age=0):
    return AuthorityDependency(source, subject, revision, status, age)


def test_h10_hr01_rollback_revision_is_currently_not_detected():
    # Hostile proposition: a previously observed revision 100 must not later accept 99.
    previously_observed_revision = 100
    replayed = d("registry", "product-x", 99, "AUTHORISED")
    assert replayed.revision < previously_observed_revision
    assert converge(DependencyBasis((replayed,))) != ConvergenceResult.ACTIVE


def test_h10_hr02_same_revision_conflicting_status_is_currently_not_detected():
    # Two observations for the same authority identity and revision disagree.
    a = d("registry-a", "product-x", 200, "AUTHORISED")
    b = d("registry-b", "product-x", 200, "REVOKED")
    assert converge(DependencyBasis((a, b))) == ConvergenceResult.INDETERMINATE


def test_h10_hr03_source_substitution_is_currently_not_detected():
    # A lookalike source is positive, but source identity has not been authenticated/allowlisted.
    substituted = d("registry-lookalike", "product-x", 300, "AUTHORISED")
    assert converge(DependencyBasis((substituted,))) != ConvergenceResult.ACTIVE
