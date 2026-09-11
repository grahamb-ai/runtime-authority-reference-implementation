from dataclasses import replace

from app.hardening.whole_stack import make_layer_authority_evidence
from tests.test_asvh_whole_stack_hostile import context, run


def _rebind_lease(lease_id):
    ctx = context()
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
            authority_lease_id=lease_id,
            runtime_policy_version=item.runtime_policy_version,
            rule_catalogue_version=item.rule_catalogue_version,
            control_contract_version=item.control_contract_version,
            deployment_profile_version=item.deployment_profile_version,
        ))
    return replace(ctx, distributed_lease_id=lease_id, layer_evidence=tuple(rebound))


def test_ws23_001_empty_authority_lease_cannot_form():
    assert run(_rebind_lease("")).status != "FORMED"


def test_ws23_002_whitespace_authority_lease_cannot_form():
    assert run(_rebind_lease("   ")).status != "FORMED"


def test_ws23_003_non_string_authority_lease_cannot_form():
    assert run(_rebind_lease(0)).status != "FORMED"


def test_ws23_004_exact_nonblank_authority_lease_remains_valid_control():
    assert run(_rebind_lease("LEASE-01")).status == "FORMED"
