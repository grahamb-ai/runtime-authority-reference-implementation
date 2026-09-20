"""HARDEN-011 third-order verification of durable/shared execution authority.

Failure-first probes. Preserve any RED before remediation.
"""
import os, shutil, tempfile
from pathlib import Path
from asvh.execution_authority import SQLiteExecutionAuthorityStore, ExecutionGateway
from tests.test_asvh_harden_011_execution_route_attack import valid_bind

def setup(path, executor="epr-writer-A", secret="executor-secret"):
    return ExecutionGateway(SQLiteExecutionAuthorityStore(path), executor, secret)

def test_h11_to01_storage_snapshot_rollback_must_not_resurrect_consumed_capability():
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/"state.db"; snap=Path(d)/"snapshot.db"; b=valid_bind(); g=setup(p)
        token=g.issue(b,"attempt-A","clinical-note")
        shutil.copy2(p,snap)  # snapshot while capability is unconsumed
        assert g.commit([],b,"attempt-A","clinical-note",token,g.executor_proof(token))=="COMMITTED"
        os.replace(snap,p)    # restore old storage image
        restarted=setup(p)
        assert restarted.commit([],b,"attempt-A","clinical-note",token,restarted.executor_proof(token))!="COMMITTED"

def test_h11_to02_missing_shared_store_must_fail_closed_not_recreate_authority():
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/"state.db"; b=valid_bind(); g=setup(p); token=g.issue(b,"attempt-A","clinical-note")
        os.remove(p)
        recreated=setup(p)
        # A missing store must not make an old externally held capability usable.
        assert recreated.commit([],b,"attempt-A","clinical-note",token,recreated.executor_proof(token))!="COMMITTED"

def test_h11_to03_wrong_executor_secret_must_not_authorise_use():
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/"state.db"; b=valid_bind(); issuer=setup(p); token=issuer.issue(b,"attempt-A","clinical-note")
        impostor=setup(p,secret="wrong-secret")
        assert impostor.commit([],b,"attempt-A","clinical-note",token,impostor.executor_proof(token))!="COMMITTED"

def test_h11_to04_wrong_executor_identity_must_not_authorise_use():
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/"state.db"; b=valid_bind(); issuer=setup(p); token=issuer.issue(b,"attempt-A","clinical-note")
        other=setup(p,executor="epr-writer-B",secret="executor-secret")
        assert other.commit([],b,"attempt-A","clinical-note",token,other.executor_proof(token))!="COMMITTED"

def test_h11_to05_consumed_before_consequence_failure_must_not_be_reusable():
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/"state.db"; b=valid_bind(); g=setup(p); token=g.issue(b,"attempt-A","clinical-note")
        # Model atomic consumption succeeding immediately before downstream formation fails.
        assert g.store.consume(token,b.digest(),"attempt-A",__import__("hashlib").sha256(b"clinical-note").hexdigest(),g.executor_id)
        # Retry must not be able to form the consequence using the consumed capability.
        assert g.commit([],b,"attempt-A","clinical-note",token,g.executor_proof(token))!="COMMITTED"
