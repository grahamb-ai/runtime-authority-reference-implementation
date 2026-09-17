"""Failure-first attacks on policy-position revalidation to consequence formation."""
from asvh.authority_convergence import ConvergenceResult


def naive_policy_check_then_commit(read_policy,commit):
    p=read_policy()
    if p.standing!="ACTIVE": return "HELD"
    return commit()


def test_h10_hr45_policy_revoked_after_revalidation_before_commit_must_not_commit():
    positions=iter([type("P",(),{"standing":"ACTIVE"})(),type("P",(),{"standing":"REVOKED"})()])
    result=naive_policy_check_then_commit(lambda:next(positions),lambda:"COMMITTED")
    assert result!="COMMITTED"


def test_h10_hr46_policy_digest_changes_after_revalidation_before_commit_must_not_commit():
    # Frozen proposition: a successful read is not a durable commit grant.
    result=naive_policy_check_then_commit(lambda:type("P",(),{"standing":"ACTIVE","digest":"a"})(),lambda:"COMMITTED")
    assert result!="COMMITTED"


def test_h10_hr47_policy_authority_unavailable_at_final_bind_must_not_commit():
    result=naive_policy_check_then_commit(lambda:type("P",(),{"standing":"ACTIVE"})(),lambda:"COMMITTED")
    assert result!="COMMITTED"


def test_h10_hr48_commit_path_requires_policy_position_binding_token_or_receipt():
    def commit_without_binding(): return "COMMITTED"
    assert commit_without_binding()!="COMMITTED"
