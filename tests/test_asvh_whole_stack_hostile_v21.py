from dataclasses import replace

from app.hardening.whole_stack import make_layer_authority_evidence
from tests.test_asvh_whole_stack_hostile import context, run
from tests.test_asvh_whole_stack_hostile_v10 import signed_bg


def _rebind_authority_basis(*, policy_version=None, rule_catalogue_version=None):
    ctx = context()
    policy = policy_version or ctx.authority_policy_version
    rules = rule_catalogue_version or ctx.authority_rule_catalogue_version
    rebound = []
    for item in ctx.layer_evidence:
        rebound.append(make_layer_authority_evidence(
            layer=item.layer,
            producer_id=item.producer_id,
            deployment_id=item.deployment_id,
            commit_binding_hash=item.commit_binding_hash,
            status=item.status,
            observed_at=item.observed_at,
            authority_epoch=item.authority_epoch,
            authority_lease_id=item.authority_lease_id,
            runtime_policy_version=policy,
            rule_catalogue_version=rules,
            control_contract_version=item.control_contract_version,
            deployment_profile_version=item.deployment_profile_version,
        ))
    return replace(
        ctx,
        authority_policy_version=policy,
        authority_rule_catalogue_version=rules,
        layer_evidence=tuple(rebound),
    )


def test_ws21_001_break_glass_cannot_form_with_authority_policy_basis_different_from_exact_commit():
    c, bg = signed_bg("BG-WS21-POLICY")
    hostile_context = _rebind_authority_basis(policy_version="HC-POL-0.9")
    assert hostile_context.authority_policy_version != c.runtime_policy_version
    assert run(hostile_context, c, decision="REFUSE", bg=bg).status != "FORMED"


def test_ws21_002_break_glass_cannot_form_with_rule_catalogue_basis_different_from_exact_commit():
    c, bg = signed_bg("BG-WS21-RULES")
    hostile_context = _rebind_authority_basis(rule_catalogue_version="ASVH-RC-0.9")
    assert hostile_context.authority_rule_catalogue_version != c.rule_catalogue_version
    assert run(hostile_context, c, decision="REFUSE", bg=bg).status != "FORMED"


def test_ws21_003_break_glass_with_current_commit_policy_basis_remains_valid_control():
    c, bg = signed_bg("BG-WS21-CONTROL")
    assert run(context(), c, decision="REFUSE", bg=bg).status == "FORMED"
