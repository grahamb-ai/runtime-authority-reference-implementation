"""ASVH-AIRP-009 — consequence-time standing dependency robustness.

Frozen before execution. Verifies fail-closed behavior for unavailable,
exceptional, indeterminate and prevented standing reads, plus ACTIVE control.
"""
import tempfile
from pathlib import Path
import pytest
from asvh.authority_convergence import ConvergenceResult
from asvh.execution_authority import SQLiteConsumptionAnchor,SQLiteExecutionAuthorityStore,ExecutionGateway,ExecutorIdentityRegistry
from tests.test_asvh_harden_011_execution_route_attack import valid_bind

def gateway(directory,reader):
    root=Path(directory)
    registry=ExecutorIdentityRegistry({"epr-writer-A":"executor-secret"})
    return ExecutionGateway(
        SQLiteExecutionAuthorityStore(root/"state.db",SQLiteConsumptionAnchor(root/"anchor.db")),
        "epr-writer-A","executor-secret",registry,reader)

def execute(reader):
    with tempfile.TemporaryDirectory() as d:
        g=gateway(d,reader); b=valid_bind("attempt-A")
        token=g.issue(b,"attempt-A","synthetic-clinical-note")
        proof=g.executor_proof(token); sink=[]
        result=g.commit(sink,b,"attempt-A","synthetic-clinical-note",token,proof)
        return result,sink

@pytest.mark.parametrize("reader",[
    lambda: ConvergenceResult.PREVENTED,
    lambda: ConvergenceResult.INDETERMINATE,
    lambda: None,
    lambda: "ACTIVE",
])
def test_non_active_or_unverifiable_standing_fails_closed(reader):
    result,sink=execute(reader)
    assert result=="BLOCKED"
    assert sink==[]

def test_standing_reader_exception_fails_closed():
    def reader(): raise RuntimeError("standing source unavailable")
    result,sink=execute(reader)
    assert result=="BLOCKED"; assert sink==[]

def test_active_current_standing_positive_control_commits():
    result,sink=execute(lambda:ConvergenceResult.ACTIVE)
    assert result=="COMMITTED"
    assert sink==[("attempt-A","synthetic-clinical-note")]

def test_no_standing_reader_is_not_fail_closed():
    # Diagnostic challenge: an unconfigured gateway currently retains legacy behavior.
    with tempfile.TemporaryDirectory() as d:
        g=gateway(d,None); b=valid_bind("attempt-A")
        token=g.issue(b,"attempt-A","synthetic-clinical-note"); proof=g.executor_proof(token); sink=[]
        result=g.commit(sink,b,"attempt-A","synthetic-clinical-note",token,proof)
        assert result=="BLOCKED", "CONFIGURATION GAP: gateway can COMMIT without a consequence-time standing reader"
        assert sink==[]
