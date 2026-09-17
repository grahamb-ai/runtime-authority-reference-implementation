"""Second-order attacks against the remediated reference final bind."""
from asvh.authority_convergence import TrustPolicyPosition,PolicyPositionVerifier,ConsequenceBind,final_bind_and_execute,ConvergenceResult

def position(rev=8,digest="d8",epoch=20,context="c",source="policy-authority",standing="ACTIVE",age=0,proof="proof"):
    return TrustPolicyPosition(rev,digest,standing,source,age,epoch,proof,context)
def verifier(fn=lambda _:True): return PolicyPositionVerifier("policy-authority","c",5,fn)
def binding():
    p=position(); return ConsequenceBind(p.policy_revision,p.policy_digest,p.authority_epoch,p.observation_context)

def test_h10_hr49_same_revision_same_digest_but_changed_standing_must_not_execute():
    assert final_bind_and_execute(expected_bind=binding(),read_policy_position=lambda:position(standing="SUSPENDED"),policy_position_verifier=verifier(),execute=lambda _:"COMMITTED")==ConvergenceResult.INDETERMINATE

def test_h10_hr50_attestation_verifier_exception_must_fail_closed():
    def boom(_): raise RuntimeError("verifier unavailable")
    try: result=final_bind_and_execute(expected_bind=binding(),read_policy_position=position,policy_position_verifier=verifier(boom),execute=lambda _:"COMMITTED")
    except RuntimeError: result="EXCEPTION_ESCAPED"
    assert result==ConvergenceResult.INDETERMINATE

def test_h10_hr51_policy_reader_exception_must_fail_closed():
    def boom(): raise RuntimeError("policy authority unavailable")
    try: result=final_bind_and_execute(expected_bind=binding(),read_policy_position=boom,policy_position_verifier=verifier(),execute=lambda _:"COMMITTED")
    except RuntimeError: result="EXCEPTION_ESCAPED"
    assert result==ConvergenceResult.INDETERMINATE

def test_h10_hr52_execute_must_receive_and_enforce_exact_bind_not_ignore_it():
    def executor(_ignored): return "COMMITTED"
    assert final_bind_and_execute(expected_bind=binding(),read_policy_position=position,policy_position_verifier=verifier(),execute=executor)!="COMMITTED"

def test_h10_hr53_binding_must_include_policy_source_identity():
    assert hasattr(binding(),"source_id") and binding().source_id=="policy-authority"

def test_h10_hr54_binding_must_include_attestation_identity_or_digest():
    assert hasattr(binding(),"attestation_digest") and bool(binding().attestation_digest)

def test_h10_hr55_policy_position_must_have_observation_nonce_or_attempt_identity():
    assert hasattr(position(),"attempt_id") and bool(position().attempt_id)
