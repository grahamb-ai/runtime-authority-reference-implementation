from app.hardening.distributed_authority import DistributedAuthorityStore
from tests.test_asvh_harden_009 import gate, grant, obs


def test_hostile_preconsequence_rejects_observation_from_other_node():
    s=DistributedAuthorityStore(); g=gate(s); gr=grant()
    assert g.activate("n1",gr,obs()).status=="ACTIVE"
    forged=obs(node="n2",ae=1,lease="L1",se=1,ss=10,policy="1.0")
    assert g.pre_consequence_check("n1",gr,forged).status=="PREVENTED"


def test_hostile_preconsequence_rejects_observation_from_other_lease():
    s=DistributedAuthorityStore(); g=gate(s); gr=grant()
    assert g.activate("n1",gr,obs()).status=="ACTIVE"
    forged=obs(node="n1",ae=1,lease="OLD-LEASE",se=1,ss=10,policy="1.0")
    assert g.pre_consequence_check("n1",gr,forged).status=="PREVENTED"


def test_hostile_negative_replica_age_is_not_fresh():
    assert gate().activate("n1",grant(),obs(age=-999)).status=="PREVENTED"


def test_hostile_observation_authority_epoch_cannot_differ_at_consequence():
    s=DistributedAuthorityStore(); g=gate(s); gr=grant()
    assert g.activate("n1",gr,obs()).status=="ACTIVE"
    forged=obs(node="n1",ae=999,lease="L1",se=1,ss=10,policy="1.0")
    assert g.pre_consequence_check("n1",gr,forged).status=="PREVENTED"
