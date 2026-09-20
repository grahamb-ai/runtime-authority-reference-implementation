"""ASVH-AIRP-006 — frozen composition challenge.

Question: can the existing consequence-time authority determination be composed
with the existing HARDEN-011 protected execution boundary without changing
either mechanism to obtain the result?

Synthetic engineering condition only. This is not an NHS consent rule and not
an official ORCHA AiRP test.
"""
import tempfile
from pathlib import Path

from asvh.authority_convergence import (
    AuthorityDependency, DependencyBasis, ConvergenceResult,
    consequence_time_converge,
)
from asvh.execution_authority import (
    SQLiteConsumptionAnchor, SQLiteExecutionAuthorityStore,
    ExecutionGateway, ExecutorIdentityRegistry,
)
from tests.test_asvh_harden_011_execution_route_attack import valid_bind


def _condition(status: str, revision: int) -> DependencyBasis:
    return DependencyBasis((
        AuthorityDependency(
            source_id="synthetic-runtime-condition-source",
            subject_id="synthetic-encounter-001",
            revision=revision,
            status=status,
            age_seconds=0,
            required=True,
        ),
    ))


def _gateway(directory: str, current_standing_reader):
    root=Path(directory)
    registry=ExecutorIdentityRegistry({"epr-writer-A":"executor-secret"})
    anchor=SQLiteConsumptionAnchor(root/"anchor.db")
    store=SQLiteExecutionAuthorityStore(root/"state.db",anchor)
    return ExecutionGateway(store,"epr-writer-A","executor-secret",registry,current_standing_reader=current_standing_reader)


def test_airp_006_state_change_cannot_reach_existing_protected_sink():
    # T0: historical observation supports proceeding at that time.
    t0_result,_=consequence_time_converge(lambda:_condition("VALID",1))
    assert t0_result==ConvergenceResult.ACTIVE

    # Existing H11 machinery can issue an execution capability for the exact
    # represented attempt/payload. We deliberately do not modify H11 for AiRP.
    with tempfile.TemporaryDirectory() as d:
        standing={"status":"VALID","revision":1}
        def read_standing():
            result,_=consequence_time_converge(lambda:_condition(standing["status"],standing["revision"]))
            return result
        gateway=_gateway(d,read_standing)
        bind=valid_bind("attempt-A")
        token=gateway.issue(bind,"attempt-A","synthetic-clinical-note")
        proof=gateway.executor_proof(token)
        sink=[]

        # T1: revalidation immediately at the modeled pre-consequence boundary.
        standing["status"]="WITHDRAWN"; standing["revision"]=2
        t1_result,t1_bind=consequence_time_converge(lambda:_condition("WITHDRAWN",2))

        # Composition rule under challenge: protected execution is invoked only
        # when current standing is ACTIVE. A PREVENTED result cannot be promoted
        # into an H11 commit.
        result="BLOCKED_BY_CURRENT_STANDING"
        if t1_result==ConvergenceResult.ACTIVE:
            result=gateway.commit(
                sink,bind,"attempt-A","synthetic-clinical-note",token,proof
            )

        assert t1_result==ConvergenceResult.PREVENTED
        assert t1_bind is None
        assert result!="COMMITTED"
        assert sink==[]


def test_airp_006_control_proves_h11_sink_was_reachable_when_current_standing_active():
    # Positive control: with current standing ACTIVE, the unchanged H11 gateway
    # can form exactly one represented commit. This prevents a vacuous blocked
    # result caused by an unreachable/broken sink.
    with tempfile.TemporaryDirectory() as d:
        gateway=_gateway(d,lambda:ConvergenceResult.ACTIVE)
        bind=valid_bind("attempt-A")
        token=gateway.issue(bind,"attempt-A","synthetic-clinical-note")
        proof=gateway.executor_proof(token)
        sink=[]

        current,_=consequence_time_converge(lambda:_condition("VALID",1))
        assert current==ConvergenceResult.ACTIVE

        result=gateway.commit(
            sink,bind,"attempt-A","synthetic-clinical-note",token,proof
        )
        assert result=="COMMITTED"
        assert sink==[("attempt-A","synthetic-clinical-note")]
