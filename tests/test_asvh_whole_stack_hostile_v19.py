from dataclasses import replace

from app.hardening.whole_stack import make_layer_authority_evidence
from tests.test_asvh_whole_stack_hostile import context, run


def _with_naive_observation(layer_name):
    ctx = context()
    rebound = []
    for item in ctx.layer_evidence:
        if item.layer == layer_name:
            rebound.append(make_layer_authority_evidence(
                layer=item.layer,
                producer_id=item.producer_id,
                deployment_id=item.deployment_id,
                commit_binding_hash=item.commit_binding_hash,
                status=item.status,
                observed_at="2026-09-11T12:00:00",
                authority_epoch=item.authority_epoch,
                authority_lease_id=item.authority_lease_id,
                runtime_policy_version=item.runtime_policy_version,
                rule_catalogue_version=item.rule_catalogue_version,
                control_contract_version=item.control_contract_version,
                deployment_profile_version=item.deployment_profile_version,
            ))
        else:
            rebound.append(item)
    return replace(ctx, layer_evidence=tuple(rebound))


def test_ws19_001_naive_distributed_observation_cannot_form():
    assert run(_with_naive_observation("DISTRIBUTED_AUTHORITY")).status != "FORMED"


def test_ws19_002_naive_recovery_observation_cannot_form():
    assert run(_with_naive_observation("RECOVERY_AUTHORITY")).status != "FORMED"


def test_ws19_003_naive_evidence_contract_observation_cannot_form():
    assert run(_with_naive_observation("EVIDENCE_CONTRACT")).status != "FORMED"


def test_ws19_004_naive_policy_observation_cannot_form():
    assert run(_with_naive_observation("POLICY_TRANSITION")).status != "FORMED"


def test_ws19_005_naive_present_standing_observation_cannot_form():
    assert run(_with_naive_observation("PRESENT_STANDING")).status != "FORMED"


def test_ws19_006_timezone_aware_composition_evidence_remains_valid_control():
    assert run(context()).status == "FORMED"
