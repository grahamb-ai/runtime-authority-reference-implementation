from dataclasses import replace
from pathlib import Path

from app.hardening.recovery_authority import AuthorityState, AuthorityTrustProfile, RecoveryAuthorityGate, RecoveryWatermarkStore


def profile(**changes):
    base = AuthorityTrustProfile("ATP-1", 1, "ASVH-TEST-01", ("RA-PRIMARY", "RA-FAILOVER"), 2)
    return replace(base, **changes)


def state(service="RA-PRIMARY", epoch=1, sequence=1, payload="AUTHORISED"):
    return AuthorityState(service, epoch, sequence, payload)


def gate(tmp_path, p=None):
    p = p or profile()
    return RecoveryAuthorityGate(p, RecoveryWatermarkStore(tmp_path / "recovery.db"))


def test_h6_001_primary_current_active(tmp_path):
    assert gate(tmp_path).evaluate(profile(), state()).status == "ACTIVE"


def test_h6_002_failover_exact_current_matching_fingerprint_active(tmp_path):
    g = gate(tmp_path); assert g.evaluate(profile(), state("RA-PRIMARY",1,1)).status == "ACTIVE"
    assert g.evaluate(profile(), state("RA-FAILOVER",1,1)).status == "ACTIVE"


def test_h6_003_lower_sequence_prevented(tmp_path):
    g=gate(tmp_path); g.evaluate(profile(), state(sequence=5)); assert g.evaluate(profile(), state("RA-FAILOVER",1,4)).status == "PREVENTED"


def test_h6_004_lower_epoch_prevented(tmp_path):
    g=gate(tmp_path); g.evaluate(profile(), state(epoch=2,sequence=1)); assert g.evaluate(profile(), state("RA-FAILOVER",1,99)).status == "PREVENTED"


def test_h6_005_same_position_different_fingerprint_prevented(tmp_path):
    g=gate(tmp_path); g.evaluate(profile(), state(payload="AUTHORISED")); r=g.evaluate(profile(), state("RA-FAILOVER",1,1,"SUSPENDED")); assert r.status == "PREVENTED" and "fingerprint" in r.reason


def test_h6_006_unknown_service_prevented(tmp_path):
    assert gate(tmp_path).evaluate(profile(), state("UNKNOWN")).status == "PREVENTED"


def test_h6_007_requester_service_prevented(tmp_path):
    assert gate(tmp_path).evaluate(profile(), state("REQUESTING_AI")).status == "PREVENTED"


def test_h6_008_store_failure_not_active(tmp_path):
    class BrokenStore:
        def read(self, deployment_id): return None
        def accept(self, deployment_id, state): raise OSError("down")
    g=RecoveryAuthorityGate(profile(), BrokenStore()); assert g.evaluate(profile(), state()).status == "INDETERMINATE"


def test_h6_009_restart_retains_watermark(tmp_path):
    db=tmp_path/"r.db"; g1=RecoveryAuthorityGate(profile(),RecoveryWatermarkStore(db)); g1.evaluate(profile(),state(sequence=10))
    g2=RecoveryAuthorityGate(profile(),RecoveryWatermarkStore(db)); assert g2.evaluate(profile(),state("RA-FAILOVER",1,9)).status == "PREVENTED"


def test_h6_010_higher_sequence_raises_watermark(tmp_path):
    g=gate(tmp_path); g.evaluate(profile(),state(sequence=1)); assert g.evaluate(profile(),state("RA-FAILOVER",1,2)).status == "ACTIVE"
    assert g.store.read(profile().deployment_id)[:2] == (1,2)


def test_h6_011_stale_primary_cannot_rollback_after_failover(tmp_path):
    g=gate(tmp_path); g.evaluate(profile(),state("RA-FAILOVER",2,5)); assert g.evaluate(profile(),state("RA-PRIMARY",2,4)).status == "PREVENTED"


def test_h6_012_profile_version_mismatch_prevented(tmp_path):
    g=gate(tmp_path); assert g.evaluate(profile(profile_version=2),state()).status == "PREVENTED"


def test_h6_013_same_version_service_set_change_prevented(tmp_path):
    g=gate(tmp_path); forged=profile(authorised_service_ids=("RA-PRIMARY","RA-FAILOVER","ATTACKER")); assert g.evaluate(forged,state("ATTACKER")).status == "PREVENTED"


def test_h6_014_same_version_independence_downgrade_prevented(tmp_path):
    g=gate(tmp_path); assert g.evaluate(profile(independence_level=1),state()).status == "PREVENTED"


def test_h6_015_authorised_profile_transition(tmp_path):
    p2=AuthorityTrustProfile("ATP-2",2,"ASVH-TEST-01",("RA-NEW",),2); g=RecoveryAuthorityGate(p2,RecoveryWatermarkStore(tmp_path/"r.db")); assert g.evaluate(p2,state("RA-NEW",1,1)).status == "ACTIVE"


def test_h6_016_malformed_position_explicit_failure(tmp_path):
    bad=AuthorityState("RA-PRIMARY","x",1,"AUTHORISED")
    assert gate(tmp_path).evaluate(profile(),bad).status == "PREVENTED"


def test_h6_017_negative_position_prevented(tmp_path):
    assert gate(tmp_path).evaluate(profile(),state(epoch=-1)).status == "PREVENTED"


def test_h6_018_repeat_valid_state_deterministic(tmp_path):
    g=gate(tmp_path); a=g.evaluate(profile(),state()); b=g.evaluate(profile(),state()); assert a.status == b.status == "ACTIVE"


def test_h6_019_evidence_reconstructs_basis(tmp_path):
    r=gate(tmp_path).evaluate(profile(),state()); assert r.service_id=="RA-PRIMARY" and r.profile_id=="ATP-1" and r.profile_version==1 and r.fingerprint and r.independence_level==2


def test_h6_020_declared_level_bounded(tmp_path):
    r=gate(tmp_path).evaluate(profile(),state()); assert r.independence_level == 2
