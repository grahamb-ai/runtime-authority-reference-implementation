from dataclasses import replace

from app.hardening.whole_stack import make_layer_authority_evidence
from tests.test_asvh_whole_stack_hostile import context, run


def _rebind_numeric_fields(*, authority_epoch=None, deployment_profile_version=None):
    ctx = context()
    epoch = ctx.current_distributed_epoch if authority_epoch is None else authority_epoch
    profile_version = 1 if deployment_profile_version is None else deployment_profile_version
    rebound = []
    for item in ctx.layer_evidence:
        rebound.append(make_layer_authority_evidence(
            layer=item.layer,
            producer_id=item.producer_id,
            deployment_id=item.deployment_id,
            commit_binding_hash=item.commit_binding_hash,
            status=item.status,
            observed_at=item.observed_at,
            authority_epoch=epoch,
            authority_lease_id=item.authority_lease_id,
            runtime_policy_version=item.runtime_policy_version,
            rule_catalogue_version=item.rule_catalogue_version,
            control_contract_version=item.control_contract_version,
            deployment_profile_version=profile_version,
        ))
    return replace(
        ctx,
        distributed_authority_epoch=epoch,
        current_distributed_epoch=epoch,
        layer_evidence=tuple(rebound),
    )


def test_ws22_001_boolean_authority_epoch_cannot_form():
    hostile = _rebind_numeric_fields(authority_epoch=True)
    assert run(hostile).status != "FORMED"


def test_ws22_002_zero_authority_epoch_cannot_form():
    hostile = _rebind_numeric_fields(authority_epoch=0)
    assert run(hostile).status != "FORMED"


def test_ws22_003_negative_authority_epoch_cannot_form():
    hostile = _rebind_numeric_fields(authority_epoch=-1)
    assert run(hostile).status != "FORMED"


def test_ws22_004_boolean_deployment_profile_version_cannot_form():
    hostile = _rebind_numeric_fields(deployment_profile_version=True)
    assert run(hostile).status != "FORMED"


def test_ws22_005_positive_integer_numeric_fences_remain_valid_control():
    valid = _rebind_numeric_fields(authority_epoch=2, deployment_profile_version=1)
    assert run(valid).status == "FORMED"
