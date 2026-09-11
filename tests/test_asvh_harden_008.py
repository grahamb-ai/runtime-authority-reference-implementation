from datetime import datetime, timezone
from dataclasses import replace

from app.hardening.policy_transition import (
    OutstandingAuthority, PolicyHighWatermark, PolicyState,
    PolicyTransition, PolicyTransitionGate,
)


class Clock:
    def __init__(self, value="2026-09-11T12:00:00Z"):
        self.value = value
    def now(self):
        return datetime.fromisoformat(self.value.replace("Z", "+00:00")).astimezone(timezone.utc)


def state(policy="2.0", rules="R2", profile="DP-1", profile_version=1):
    return PolicyState("HC-POLICY", policy, rules, profile, profile_version)


def authority(policy="1.0", rules="R1", **kw):
    base = dict(
        authority_id="AUTH-1", policy_id="HC-POLICY", policy_version=policy,
        ruleset_version=rules, deployment_profile_id="DP-1", deployment_profile_version=1,
        exact_commit_hash="abc123", issued_at="2026-09-11T10:00:00Z",
        expires_at="2026-09-11T14:00:00Z", invalidated=False, break_glass=False,
    )
    base.update(kw)
    return OutstandingAuthority(**base)


def transition(cls="REVALIDATE", compatible=False, effective="2026-09-11T11:00:00Z", **kw):
    base = dict(
        transition_id="PT-1", from_policy_version="1.0", to_policy_version="2.0",
        from_ruleset_version="R1", to_ruleset_version="R2",
        deployment_profile_id="DP-1", deployment_profile_version=1,
        effective_at=effective, transition_class=cls,
        compatibility_explicit=compatible, reason="synthetic transition",
        break_glass_compatible=False,
    )
    base.update(kw)
    return PolicyTransition(**base)


def gate(clock=None):
    return PolicyTransitionGate(PolicyHighWatermark(), clock or Clock())


def test_h8_001_unchanged_policy_allows():
    g=gate(); a=authority("1.0","R1"); s=state("1.0","R1")
    assert g.evaluate(a,s,None).status == "ALLOW"


def test_h8_002_explicit_non_material_compatible_allows():
    assert gate().evaluate(authority(), state(), transition("NON_MATERIAL", True)).status == "ALLOW"


def test_h8_003_non_material_without_explicit_compatibility_not_allow():
    assert gate().evaluate(authority(), state(), transition("NON_MATERIAL", False)).status == "PREVENTED"


def test_h8_004_revalidate_blocks_old_pending_new_determination():
    r=gate().evaluate(authority(), state(), transition("REVALIDATE"))
    assert r.status == "REVALIDATE" and r.revalidation_required


def test_h8_005_successful_revalidation_creates_new_basis():
    g=gate(); old=authority(); new=g.revalidate(old,state(),"AUTH-2","2026-09-11T12:01:00Z","2026-09-11T13:00:00Z")
    assert new.authority_id != old.authority_id and (new.policy_version,new.ruleset_version)==("2.0","R2") and old.policy_version=="1.0"


def test_h8_006_invalidate_prevents_old():
    assert gate().evaluate(authority(),state(),transition("INVALIDATE")).status == "PREVENTED"


def test_h8_007_missing_transition_semantics_not_allow():
    assert gate().evaluate(authority(),state(),None).status == "INDETERMINATE"


def test_h8_008_future_transition_not_apply_before_effective():
    g=gate(Clock("2026-09-11T10:30:00Z")); a=authority("1.0","R1"); s=state("1.0","R1")
    t=transition("INVALIDATE", effective="2026-09-11T11:00:00Z", to_policy_version="1.0", to_ruleset_version="R1")
    assert g.evaluate(a,s,t).status == "ALLOW"


def test_h8_009_transition_applies_at_effective_time():
    g=gate(Clock("2026-09-11T11:00:00Z"))
    assert g.evaluate(authority(),state(),transition("INVALIDATE",effective="2026-09-11T11:00:00Z")).status == "PREVENTED"


def test_h8_010_caller_time_cannot_override_trusted_clock():
    g=gate(Clock("2026-09-11T12:00:00Z"))
    assert g.evaluate(authority(),state(),transition("INVALIDATE",effective="2026-09-11T11:30:00Z")).status == "PREVENTED"


def test_h8_011_ruleset_change_same_policy_requires_transition():
    assert gate().evaluate(authority("1.0","R1"),state("1.0","R2"),None).status == "INDETERMINATE"


def test_h8_012_deployment_profile_mismatch_rejected():
    assert gate().evaluate(authority(),state(profile="DP-2"),transition()).status == "PREVENTED"


def test_h8_013_old_policy_replay_after_invalidation_cannot_resurrect():
    g=gate(); a=authority(); assert g.evaluate(a,state(),transition("INVALIDATE")).status=="PREVENTED"
    assert g.evaluate(a,state("1.0","R1"),None).status=="PREVENTED"


def test_h8_014_policy_rollback_after_newer_state_not_resurrect():
    g=gate(); a=authority(); g.evaluate(a,state(),transition("REVALIDATE"))
    assert g.evaluate(a,state("1.0","R1"),None).status == "PREVENTED"


def test_h8_015_expiry_beats_compatibility():
    g=gate(Clock("2026-09-11T15:00:00Z")); a=authority(expires_at="2026-09-11T14:00:00Z")
    assert g.evaluate(a,state(),transition("NON_MATERIAL",True)).status=="PREVENTED"


def test_h8_016_contradictory_transition_identity_fails_explicitly():
    g=gate(); a=authority(); t1=transition("REVALIDATE"); g.evaluate(a,state(),t1)
    t2=replace(t1, transition_class="NON_MATERIAL", compatibility_explicit=True)
    assert g.evaluate(a,state(),t2).status=="INDETERMINATE"


def test_h8_017_malformed_transition_timestamp_fails_explicitly():
    assert gate().evaluate(authority(),state(),transition(effective="not-a-time")).status=="INDETERMINATE"


def test_h8_018_historical_authority_immutable_after_revalidation():
    g=gate(); old=authority(); _=g.revalidate(old,state(),"AUTH-2","2026-09-11T12:01:00Z","2026-09-11T13:00:00Z")
    assert old.policy_version=="1.0" and old.authority_id=="AUTH-1"


def test_h8_019_break_glass_separate_transition_semantics():
    a=authority(break_glass=True)
    assert gate().evaluate(a,state(),transition("NON_MATERIAL",True)).status=="PREVENTED"


def test_h8_020_deterministic_same_inputs_same_outcome():
    r1=gate().evaluate(authority(),state(),transition("REVALIDATE"))
    r2=gate().evaluate(authority(),state(),transition("REVALIDATE"))
    assert r1 == r2
