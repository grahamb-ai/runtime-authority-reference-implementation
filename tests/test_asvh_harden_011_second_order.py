"""ASVH HARDEN-011 second-order verification of the route-closure remediation.

These probes intentionally test properties not established by the initial 10/10
remediation verification. A RED is evidence, not a reason to weaken the probe.
"""
import threading
from tests.test_asvh_harden_011_execution_route_attack import ProtectedSink, valid_bind


def test_h11_so01_capability_for_attempt_a_cannot_authorise_attempt_b():
    sink=ProtectedSink(); bind=valid_bind("attempt-A")
    cap=sink._issue(bind,"attempt-A","clinical-note")
    assert sink.commit("attempt-B","clinical-note",capability=cap) != "COMMITTED"
    assert sink.commits == []


def test_h11_so02_capability_cannot_authorise_substituted_payload():
    sink=ProtectedSink(); bind=valid_bind()
    cap=sink._issue(bind,"attempt-A","clinical-note")
    assert sink.commit("attempt-A","different-note",capability=cap) != "COMMITTED"
    assert sink.commits == []


def test_h11_so03_stolen_capability_with_exact_tuple_is_not_sufficient():
    sink=ProtectedSink(); bind=valid_bind()
    stolen=sink._issue(bind,"attempt-A","clinical-note")
    # Possession alone must not be the entire executor authority boundary.
    result=sink.commit("attempt-A","clinical-note",capability=stolen)
    assert result != "COMMITTED"
    assert sink.commits == []


def test_h11_so04_restart_must_not_resurrect_consumed_capability():
    first=ProtectedSink(); bind=valid_bind()
    cap=first._issue(bind,"attempt-A","clinical-note")
    assert first.commit("attempt-A","clinical-note",capability=cap)=="COMMITTED"
    restarted=ProtectedSink()
    # Model restart/reconstruction with the issued capability known externally.
    restarted._issued[cap]=(bind.digest(),"attempt-A",__import__("hashlib").sha256(b"clinical-note").hexdigest())
    assert restarted.commit("attempt-A","clinical-note",capability=cap) != "COMMITTED"


def test_h11_so05_concurrent_consumption_must_form_at_most_one_commit():
    sink=ProtectedSink(); bind=valid_bind()
    cap=sink._issue(bind,"attempt-A","clinical-note")
    barrier=threading.Barrier(3); results=[]
    def worker():
        barrier.wait()
        results.append(sink.commit("attempt-A","clinical-note",capability=cap))
    a=threading.Thread(target=worker); b=threading.Thread(target=worker)
    a.start(); b.start(); barrier.wait(); a.join(); b.join()
    assert results.count("COMMITTED") <= 1
    assert len(sink.commits) <= 1


def test_h11_so06_alternate_instance_must_not_independently_accept_same_capability():
    primary=ProtectedSink(); alternate=ProtectedSink(); bind=valid_bind()
    cap=primary._issue(bind,"attempt-A","clinical-note")
    # Two executor instances sharing a route must share consumption/issuance truth.
    alternate._issued[cap]=primary._issued[cap]
    r1=primary.commit("attempt-A","clinical-note",capability=cap)
    r2=alternate.commit("attempt-A","clinical-note",capability=cap)
    assert not (r1=="COMMITTED" and r2=="COMMITTED")
    assert len(primary.commits)+len(alternate.commits) <= 1
