from dataclasses import replace
from datetime import datetime, timedelta

from app.hardening.whole_stack import make_layer_authority_evidence
from tests.test_asvh_whole_stack_hostile import context, run
from tests.test_asvh_whole_stack_hostile_v10 import signed_bg


def _fresh_context_at(now):
    """Rebind otherwise-valid composition evidence to the execution instant.

    Pass-18 originally reused context() whose layer evidence is fixed at 12:00Z.
    Moving execution to the break-glass issue/expiry boundaries therefore tested
    stale/future composition evidence rather than the intended break-glass
    boundary semantics. This helper preserves every existing binding/status but
    gives each layer fresh, integrity-bound observed_at evidence for the target
    execution instant.
    """
    ctx = context()
    rebound = []
    for item in ctx.layer_evidence:
        rebound.append(make_layer_authority_evidence(
            layer=item.layer,
            producer_id=item.producer_id,
            deployment_id=item.deployment_id,
            commit_binding_hash=item.commit_binding_hash,
            status=item.status,
            observed_at=now.isoformat(),
            authority_epoch=item.authority_epoch,
            authority_lease_id=item.authority_lease_id,
            runtime_policy_version=item.runtime_policy_version,
            rule_catalogue_version=item.rule_catalogue_version,
            control_contract_version=item.control_contract_version,
            deployment_profile_version=item.deployment_profile_version,
        ))
    return replace(ctx, layer_evidence=tuple(rebound))


def test_ws18_001_break_glass_is_expired_at_exact_expiry_boundary():
    c, bg = signed_bg("BG-WS18-EXPIRY")
    expiry = datetime.fromisoformat(bg.expires_at)
    assert run(_fresh_context_at(expiry), c, decision="REFUSE", bg=bg, now=expiry).status != "FORMED"


def test_ws18_002_break_glass_remains_valid_immediately_before_expiry():
    c, bg = signed_bg("BG-WS18-BEFORE")
    expiry = datetime.fromisoformat(bg.expires_at)
    now = expiry - timedelta(microseconds=1)
    assert run(_fresh_context_at(now), c, decision="REFUSE", bg=bg, now=now).status == "FORMED"


def test_ws18_003_break_glass_is_valid_at_exact_issue_boundary():
    c, bg = signed_bg("BG-WS18-ISSUED")
    issued = datetime.fromisoformat(bg.issued_at)
    assert run(_fresh_context_at(issued), c, decision="REFUSE", bg=bg, now=issued).status == "FORMED"
