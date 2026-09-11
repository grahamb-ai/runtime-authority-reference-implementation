from datetime import datetime, timezone, timedelta
from pathlib import Path

from app.hardening.distributed_authority import (
    DistributedAuthorityGate, DistributedAuthorityGrant, DistributedAuthorityStore, NodeObservation
)


class Clock:
    def __init__(self, value="2026-09-11T15:00:00Z"):
        self.value=value
    def now(self):
        return self.value


def grant(node="n1", ae=1, lease="L1", se=1, ss=10, policy="1.0", issued="2026-09-11T14:59:00Z", expires="2026-09-11T15:05:00Z", cluster="c1", deployment="d1", role="EXECUTION_AUTHORITY"):
    return DistributedAuthorityGrant(cluster,deployment,node,ae,lease,issued,expires,se,ss,policy,role)


def obs(node="n1", ae=1, lease="L1", se=1, ss=10, policy="1.0", observed="2026-09-11T15:00:00Z", age=0):
    return NodeObservation(node,ae,se,ss,policy,lease,observed,age)


def gate(store=None, clock=None):
    return DistributedAuthorityGate(store or DistributedAuthorityStore(), clock or Clock(), cluster_id="c1", deployment_profile_id="d1", max_replica_age_seconds=30)


def test_h9_001_single_valid_leader_active():
    assert gate().activate("n1",grant(),obs()).status=="ACTIVE"


def test_h9_002_lower_epoch_fenced_after_higher():
    s=DistributedAuthorityStore(); g=gate(s)
    assert g.activate("n2",grant("n2",2,"L2"),obs("n2",2,"L2")).status=="ACTIVE"
    assert g.activate("n1",grant(),obs()).status=="PREVENTED"


def test_h9_003_expired_lease_prevented():
    assert gate().activate("n1",grant(expires="2026-09-11T14:59:59Z"),obs()).status=="PREVENTED"


def test_h9_004_future_grant_prevented():
    assert gate().activate("n1",grant(issued="2026-09-11T15:01:00Z"),obs()).status=="PREVENTED"


def test_h9_005_wrong_cluster_prevented():
    assert gate().activate("n1",grant(cluster="c2"),obs()).status=="PREVENTED"


def test_h9_006_wrong_deployment_prevented():
    assert gate().activate("n1",grant(deployment="d2"),obs()).status=="PREVENTED"


def test_h9_007_wrong_node_prevented():
    assert gate().activate("n2",grant("n1"),obs("n2")).status=="PREVENTED"


def test_h9_008_wrong_role_prevented():
    assert gate().activate("n1",grant(role="OBSERVER"),obs()).status=="PREVENTED"


def test_h9_009_new_leadership_cannot_hide_stale_state():
    s=DistributedAuthorityStore(); g=gate(s)
    assert g.activate("n1",grant(se=2,ss=20),obs(se=2,ss=20)).status=="ACTIVE"
    assert g.activate("n2",grant("n2",2,"L2",se=1,ss=99),obs("n2",2,"L2",se=1,ss=99)).status=="PREVENTED"


def test_h9_010_state_rollback_after_activation_prevents_consequence():
    s=DistributedAuthorityStore(); g=gate(s); gr=grant(); assert g.activate("n1",gr,obs()).status=="ACTIVE"
    assert g.pre_consequence_check("n1",gr,obs(se=0,ss=99)).status=="PREVENTED"


def test_h9_011_policy_rollback_after_activation_prevents_consequence():
    s=DistributedAuthorityStore(); g=gate(s); gr=grant(policy="2.0"); assert g.activate("n1",gr,obs(policy="2.0")).status=="ACTIVE"
    assert g.pre_consequence_check("n1",gr,obs(policy="1.0")).status=="PREVENTED"


def test_h9_012_new_epoch_after_claim_fences_old_node():
    s=DistributedAuthorityStore(); g=gate(s); old=grant(); assert g.activate("n1",old,obs()).status=="ACTIVE"
    assert g.activate("n2",grant("n2",2,"L2"),obs("n2",2,"L2")).status=="ACTIVE"
    assert g.pre_consequence_check("n1",old,obs()).status=="PREVENTED"


def test_h9_013_same_epoch_different_lease_conflict():
    s=DistributedAuthorityStore(); g=gate(s); assert g.activate("n1",grant(),obs()).status=="ACTIVE"
    assert g.activate("n2",grant("n2",1,"L2"),obs("n2",1,"L2")).status=="PREVENTED"


def test_h9_014_identical_repeated_grant_idempotent():
    s=DistributedAuthorityStore(); g=gate(s)
    assert g.activate("n1",grant(),obs()).status=="ACTIVE"
    assert g.activate("n1",grant(),obs()).status=="ACTIVE"


def test_h9_015_malformed_epoch_explicit():
    bad=grant(ae=True)
    assert gate().activate("n1",bad,obs(ae=True)).status=="INDETERMINATE"


def test_h9_016_malformed_temporal_state_explicit():
    assert gate().activate("n1",grant(expires="not-a-time"),obs()).status=="INDETERMINATE"


def test_h9_017_authority_service_outage_no_self_promotion():
    assert gate().activate("n1",grant(),obs(),authority_service_available=False).status=="INDETERMINATE"


def test_h9_018_conflicting_same_epoch_nodes_not_both_active():
    s=DistributedAuthorityStore(); g=gate(s)
    a=g.activate("n1",grant(),obs()); b=g.activate("n2",grant("n2",1,"L2"),obs("n2",1,"L2"))
    assert [a.status,b.status].count("ACTIVE")==1


def test_h9_019_newer_current_leader_replaces_prior():
    s=DistributedAuthorityStore(); g=gate(s)
    assert g.activate("n1",grant(),obs()).status=="ACTIVE"
    assert g.activate("n2",grant("n2",2,"L2",se=2,ss=1,policy="2.0"),obs("n2",2,"L2",se=2,ss=1,policy="2.0")).status=="ACTIVE"


def test_h9_020_restart_preserves_watermarks(tmp_path):
    db=tmp_path/"dist.db"
    s1=DistributedAuthorityStore(db); g1=gate(s1); assert g1.activate("n2",grant("n2",3,"L3",se=4,ss=5,policy="3.0"),obs("n2",3,"L3",se=4,ss=5,policy="3.0")).status=="ACTIVE"; s1.close()
    s2=DistributedAuthorityStore(db); g2=gate(s2)
    assert g2.activate("n1",grant("n1",2,"L2",se=4,ss=5,policy="3.0"),obs("n1",2,"L2",se=4,ss=5,policy="3.0")).status=="PREVENTED"
    s2.close()
