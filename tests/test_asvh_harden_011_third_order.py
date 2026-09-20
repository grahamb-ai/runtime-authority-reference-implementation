"""HARDEN-011 third-order verification after structural remediation."""
import os, shutil, tempfile, hashlib
from pathlib import Path
from asvh.execution_authority import SQLiteExecutionAuthorityStore, SQLiteConsumptionAnchor, ExecutionGateway, ExecutorIdentityRegistry
from tests.test_asvh_harden_011_execution_route_attack import valid_bind

def setup(path, anchor_path, executor="epr-writer-A", secret="executor-secret", registry=None):
    anchor=SQLiteConsumptionAnchor(anchor_path)
    registry=registry or ExecutorIdentityRegistry({"epr-writer-A":"executor-secret"})
    return ExecutionGateway(SQLiteExecutionAuthorityStore(path,anchor),executor,secret,registry)

def test_h11_to01_storage_snapshot_rollback_must_not_resurrect_consumed_capability():
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/"state.db"; a=Path(d)/"anchor.db"; snap=Path(d)/"snapshot.db"; b=valid_bind(); g=setup(p,a)
        token=g.issue(b,"attempt-A","clinical-note")
        shutil.copy2(p,snap)
        assert g.commit([],b,"attempt-A","clinical-note",token,g.executor_proof(token))=="COMMITTED"
        os.replace(snap,p)
        restarted=setup(p,a)
        assert restarted.commit([],b,"attempt-A","clinical-note",token,restarted.executor_proof(token))!="COMMITTED"

def test_h11_to02_missing_shared_store_must_fail_closed_not_recreate_authority():
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/"state.db"; a=Path(d)/"anchor.db"; b=valid_bind(); g=setup(p,a); token=g.issue(b,"attempt-A","clinical-note")
        os.remove(p); recreated=setup(p,a)
        assert recreated.commit([],b,"attempt-A","clinical-note",token,recreated.executor_proof(token))!="COMMITTED"

def test_h11_to03_wrong_executor_secret_must_not_authorise_use():
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/"state.db"; a=Path(d)/"anchor.db"; b=valid_bind()
        registry=ExecutorIdentityRegistry({"epr-writer-A":"executor-secret"})
        issuer=setup(p,a,registry=registry); token=issuer.issue(b,"attempt-A","clinical-note")
        impostor=setup(p,a,secret="wrong-secret",registry=registry)
        assert impostor.commit([],b,"attempt-A","clinical-note",token,impostor.executor_proof(token))!="COMMITTED"

def test_h11_to04_wrong_executor_identity_must_not_authorise_use():
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/"state.db"; a=Path(d)/"anchor.db"; b=valid_bind()
        registry=ExecutorIdentityRegistry({"epr-writer-A":"executor-secret","epr-writer-B":"executor-secret"})
        issuer=setup(p,a,registry=registry); token=issuer.issue(b,"attempt-A","clinical-note")
        other=setup(p,a,executor="epr-writer-B",registry=registry)
        assert other.commit([],b,"attempt-A","clinical-note",token,other.executor_proof(token))!="COMMITTED"

def test_h11_to05_consumed_before_consequence_failure_must_not_be_reusable():
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/"state.db"; a=Path(d)/"anchor.db"; b=valid_bind(); g=setup(p,a); token=g.issue(b,"attempt-A","clinical-note")
        assert g.store.consume(token,b.digest(),"attempt-A",hashlib.sha256(b"clinical-note").hexdigest(),g.executor_id)
        assert g.commit([],b,"attempt-A","clinical-note",token,g.executor_proof(token))!="COMMITTED"
