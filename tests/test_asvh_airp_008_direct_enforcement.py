"""ASVH-AIRP-008 — direct enforcement challenge, frozen before execution.

Can a caller holding an exact valid H11 capability formed while T0 standing was
ACTIVE still drive the protected sink after consequence-time standing changes
to PREVENTED, by calling the H11 gateway directly?
"""
import tempfile
from pathlib import Path
from asvh.authority_convergence import AuthorityDependency,DependencyBasis,ConvergenceResult,consequence_time_converge
from asvh.execution_authority import SQLiteConsumptionAnchor,SQLiteExecutionAuthorityStore,ExecutionGateway,ExecutorIdentityRegistry
from tests.test_asvh_harden_011_execution_route_attack import valid_bind

def condition(status,revision):
    return DependencyBasis((AuthorityDependency(
        source_id="synthetic-runtime-condition-source",
        subject_id="synthetic-encounter-001",
        revision=revision,status=status,age_seconds=0,required=True),))

def gateway(directory):
    root=Path(directory)
    registry=ExecutorIdentityRegistry({"epr-writer-A":"executor-secret"})
    anchor=SQLiteConsumptionAnchor(root/"anchor.db")
    store=SQLiteExecutionAuthorityStore(root/"state.db",anchor)
    return ExecutionGateway(store,"epr-writer-A","executor-secret",registry)

def test_airp_008_prevented_current_standing_must_survive_direct_gateway_call():
    t0,_=consequence_time_converge(lambda:condition("VALID",1))
    assert t0==ConvergenceResult.ACTIVE
    with tempfile.TemporaryDirectory() as d:
        g=gateway(d); b=valid_bind("attempt-A")
        token=g.issue(b,"attempt-A","synthetic-clinical-note")
        proof=g.executor_proof(token)
        t1,_=consequence_time_converge(lambda:condition("WITHDRAWN",2))
        assert t1==ConvergenceResult.PREVENTED
        sink=[]
        # Hostile direct call deliberately bypasses AIRP-006's cooperative outer branch.
        result=g.commit(sink,b,"attempt-A","synthetic-clinical-note",token,proof)
        assert result!="COMMITTED", "ENFORCEMENT COMPOSITION FAILURE: stale T0 capability committed after T1 PREVENTED"
        assert sink==[]
