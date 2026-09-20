"""HARDEN-011 fourth-order verification.

Tests limits beyond the 246-green reference-model chain. Failure-first.
"""
import os, shutil, tempfile
from pathlib import Path
from asvh.execution_authority import SQLiteExecutionAuthorityStore, SQLiteConsumptionAnchor, ExecutionGateway, ExecutorIdentityRegistry
from tests.test_asvh_harden_011_execution_route_attack import valid_bind

def setup(state,anchor,registry=None,secret="executor-secret"):
    registry=registry or ExecutorIdentityRegistry({"epr-writer-A":"executor-secret"})
    return ExecutionGateway(SQLiteExecutionAuthorityStore(state,SQLiteConsumptionAnchor(anchor)),
                            "epr-writer-A",secret,registry)

def test_h11_fo01_correlated_rollback_of_state_and_anchor_must_not_resurrect_consumed_authority():
    with tempfile.TemporaryDirectory() as d:
        p=Path(d); state=p/"state.db"; anchor=p/"anchor.db"; ss=p/"state.snap"; aa=p/"anchor.snap"
        b=valid_bind(); g=setup(state,anchor); token=g.issue(b,"attempt-A","clinical-note")
        shutil.copy2(state,ss); shutil.copy2(anchor,aa)
        assert g.commit([],b,"attempt-A","clinical-note",token,g.executor_proof(token))=="COMMITTED"
        os.replace(ss,state); os.replace(aa,anchor)
        restarted=setup(state,anchor)
        assert restarted.commit([],b,"attempt-A","clinical-note",token,restarted.executor_proof(token))!="COMMITTED"

def test_h11_fo02_trust_registry_mutation_must_not_make_old_capability_usable_by_new_secret():
    with tempfile.TemporaryDirectory() as d:
        p=Path(d); state=p/"state.db"; anchor=p/"anchor.db"; b=valid_bind()
        original=ExecutorIdentityRegistry({"epr-writer-A":"executor-secret"})
        issuer=setup(state,anchor,original); token=issuer.issue(b,"attempt-A","clinical-note")
        mutated=ExecutorIdentityRegistry({"epr-writer-A":"attacker-secret"})
        attacker=setup(state,anchor,mutated,secret="attacker-secret")
        assert attacker.commit([],b,"attempt-A","clinical-note",token,attacker.executor_proof(token))!="COMMITTED"

def test_h11_fo03_loss_of_consumption_anchor_must_fail_closed_for_existing_capability():
    with tempfile.TemporaryDirectory() as d:
        p=Path(d); state=p/"state.db"; anchor=p/"anchor.db"; b=valid_bind(); g=setup(state,anchor)
        token=g.issue(b,"attempt-A","clinical-note")
        os.remove(anchor)
        restarted=setup(state,anchor)
        assert restarted.commit([],b,"attempt-A","clinical-note",token,restarted.executor_proof(token))!="COMMITTED"

def test_h11_fo04_failed_external_formation_requires_explicit_unresolved_outcome_not_silent_success():
    # Current reference API returns COMMITTED immediately after consumption + local append.
    # It has no durable outcome state representing consumed-but-external-consequence-unconfirmed.
    with tempfile.TemporaryDirectory() as d:
        p=Path(d); b=valid_bind(); g=setup(p/"state.db",p/"anchor.db"); token=g.issue(b,"attempt-A","clinical-note")
        local=[]
        result=g.commit(local,b,"attempt-A","clinical-note",token,g.executor_proof(token))
        assert result in {"UNRESOLVED","CONSEQUENCE_CONFIRMED"}
        assert result!="COMMITTED"
