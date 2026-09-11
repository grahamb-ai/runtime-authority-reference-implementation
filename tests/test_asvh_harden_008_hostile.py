from dataclasses import replace

from app.hardening.policy_transition import PolicyHighWatermark, PolicyTransitionGate
from tests.test_asvh_harden_008 import Clock, authority, state, transition


def test_hostile_invalidation_survives_gate_restart_with_shared_watermark():
    wm=PolicyHighWatermark(); a=authority()
    g1=PolicyTransitionGate(wm,Clock()); assert g1.evaluate(a,state(),transition("INVALIDATE")).status=="PREVENTED"
    g2=PolicyTransitionGate(wm,Clock()); assert g2.evaluate(a,state("1.0","R1"),None).status=="PREVENTED"


def test_hostile_semantic_policy_version_rollback_not_lexical():
    wm=PolicyHighWatermark(); g=PolicyTransitionGate(wm,Clock())
    # Establish policy 10.0, then attempt rollback to 2.0. Lexical string comparison would get this wrong.
    high=state("10.0","R10"); wm.accept_policy(high)
    a=authority(policy="2.0",rules="R2")
    assert g.evaluate(a,state("2.0","R2"),None).status=="PREVENTED"


def test_hostile_same_transition_id_different_effective_time_rejected():
    g=PolicyTransitionGate(PolicyHighWatermark(),Clock()); a=authority()
    t1=transition("REVALIDATE")
    assert g.evaluate(a,state(),t1).status=="REVALIDATE"
    t2=replace(t1,effective_at="2026-09-11T13:00:00Z")
    assert g.evaluate(a,state(),t2).status=="INDETERMINATE"


def test_hostile_break_glass_requires_separate_compatibility():
    g=PolicyTransitionGate(PolicyHighWatermark(),Clock()); a=authority(break_glass=True)
    t=transition("NON_MATERIAL",True,break_glass_compatible=False)
    assert g.evaluate(a,state(),t).status=="PREVENTED"
