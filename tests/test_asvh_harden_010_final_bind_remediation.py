from asvh.authority_convergence import TrustPolicyPosition,PolicyPositionVerifier,bind_from_position,final_bind_and_execute,ConvergenceResult

def p(**kw):
    d=dict(policy_revision=7,policy_digest="d7",standing="ACTIVE",source_id="policy-authority",age_seconds=0,authority_epoch=11,attestation="proof",observation_context="commit-1",attempt_id="attempt-1"); d.update(kw); return TrustPolicyPosition(**d)
def v(**kw):
    d=dict(authoritative_source_id="policy-authority",expected_context="commit-1",max_age_seconds=5,verify_attestation=lambda _:True,expected_attempt_id="attempt-1"); d.update(kw); return PolicyPositionVerifier(**d)
def bind(): return bind_from_position(p())

def test_r11_valid_final_bind_executes(): assert final_bind_and_execute(expected_bind=bind(),read_policy_position=p,policy_position_verifier=v(),execute=lambda _:"COMMITTED")=="COMMITTED"
def test_r12_source_substitution_fails_closed(): assert final_bind_and_execute(expected_bind=bind(),read_policy_position=lambda:p(source_id="lookalike"),policy_position_verifier=v(),execute=lambda _:"COMMITTED")==ConvergenceResult.INDETERMINATE
def test_r13_stale_position_fails_closed(): assert final_bind_and_execute(expected_bind=bind(),read_policy_position=lambda:p(age_seconds=6),policy_position_verifier=v(),execute=lambda _:"COMMITTED")==ConvergenceResult.INDETERMINATE
def test_r14_negative_age_fails_closed(): assert final_bind_and_execute(expected_bind=bind(),read_policy_position=lambda:p(age_seconds=-1),policy_position_verifier=v(),execute=lambda _:"COMMITTED")==ConvergenceResult.INDETERMINATE
def test_r15_revoked_position_fails_closed(): assert final_bind_and_execute(expected_bind=bind(),read_policy_position=lambda:p(standing="REVOKED"),policy_position_verifier=v(),execute=lambda _:"COMMITTED")==ConvergenceResult.INDETERMINATE
def test_r16_digest_change_fails_closed(): assert final_bind_and_execute(expected_bind=bind(),read_policy_position=lambda:p(policy_digest="d8"),policy_position_verifier=v(),execute=lambda _:"COMMITTED")==ConvergenceResult.INDETERMINATE
def test_r17_epoch_change_fails_closed(): assert final_bind_and_execute(expected_bind=bind(),read_policy_position=lambda:p(authority_epoch=12),policy_position_verifier=v(),execute=lambda _:"COMMITTED")==ConvergenceResult.INDETERMINATE
def test_r18_context_change_fails_closed(): assert final_bind_and_execute(expected_bind=bind(),read_policy_position=lambda:p(observation_context="commit-2"),policy_position_verifier=v(),execute=lambda _:"COMMITTED")==ConvergenceResult.INDETERMINATE
def test_r19_bad_attestation_fails_closed(): assert final_bind_and_execute(expected_bind=bind(),read_policy_position=p,policy_position_verifier=v(verify_attestation=lambda _:False),execute=lambda _:"COMMITTED")==ConvergenceResult.INDETERMINATE
def test_r20_missing_bind_fails_closed(): assert final_bind_and_execute(expected_bind=None,read_policy_position=p,policy_position_verifier=v(),execute=lambda _:"COMMITTED")==ConvergenceResult.INDETERMINATE
