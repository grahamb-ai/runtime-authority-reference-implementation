"""HARDEN-011 second-order verification — unchanged propositions, remediated boundary."""
import tempfile, threading
from pathlib import Path
from asvh.execution_authority import SQLiteExecutionAuthorityStore, ExecutionGateway
from tests.test_asvh_harden_011_execution_route_attack import valid_bind

def setup(path,executor="epr-writer-A",secret="executor-secret"):
    return ExecutionGateway(SQLiteExecutionAuthorityStore(path),executor,secret)

def test_h11_so01_capability_for_attempt_a_cannot_authorise_attempt_b():
    with tempfile.TemporaryDirectory() as d:
        g=setup(Path(d)/"x.db"); b=valid_bind("attempt-A"); token=g.issue(b,"attempt-A","clinical-note")
        assert g.commit([],b,"attempt-B","clinical-note",token,g.executor_proof(token))!="COMMITTED"

def test_h11_so02_capability_cannot_authorise_substituted_payload():
    with tempfile.TemporaryDirectory() as d:
        g=setup(Path(d)/"x.db"); b=valid_bind(); token=g.issue(b,"attempt-A","clinical-note")
        assert g.commit([],b,"attempt-A","different-note",token,g.executor_proof(token))!="COMMITTED"

def test_h11_so03_stolen_capability_with_exact_tuple_is_not_sufficient():
    with tempfile.TemporaryDirectory() as d:
        g=setup(Path(d)/"x.db"); b=valid_bind(); token=g.issue(b,"attempt-A","clinical-note")
        # Token possession without the executor proof is insufficient.
        assert g.commit([],b,"attempt-A","clinical-note",token,"stolen-token-only")!="COMMITTED"

def test_h11_so04_restart_must_not_resurrect_consumed_capability():
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/"x.db"; b=valid_bind(); first=setup(p); token=first.issue(b,"attempt-A","clinical-note")
        assert first.commit([],b,"attempt-A","clinical-note",token,first.executor_proof(token))=="COMMITTED"
        restarted=setup(p)
        assert restarted.commit([],b,"attempt-A","clinical-note",token,restarted.executor_proof(token))!="COMMITTED"

def test_h11_so05_concurrent_consumption_must_form_at_most_one_commit():
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/"x.db"; b=valid_bind(); g1=setup(p); token=g1.issue(b,"attempt-A","clinical-note")
        g2=setup(p); barrier=threading.Barrier(3); results=[]; sinks=[[],[]]
        def worker(g,s):
            barrier.wait(); results.append(g.commit(s,b,"attempt-A","clinical-note",token,g.executor_proof(token)))
        a=threading.Thread(target=worker,args=(g1,sinks[0])); c=threading.Thread(target=worker,args=(g2,sinks[1]))
        a.start(); c.start(); barrier.wait(); a.join(); c.join()
        assert results.count("COMMITTED")<=1
        assert sum(len(x) for x in sinks)<=1

def test_h11_so06_alternate_instance_must_not_independently_accept_same_capability():
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/"x.db"; b=valid_bind(); primary=setup(p); alternate=setup(p)
        token=primary.issue(b,"attempt-A","clinical-note"); s1=[];s2=[]
        r1=primary.commit(s1,b,"attempt-A","clinical-note",token,primary.executor_proof(token))
        r2=alternate.commit(s2,b,"attempt-A","clinical-note",token,alternate.executor_proof(token))
        assert not(r1=="COMMITTED" and r2=="COMMITTED")
        assert len(s1)+len(s2)<=1
