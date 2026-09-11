from dataclasses import replace
from datetime import datetime, timedelta, timezone

from app.hardening.evidence_contract import (
    EvidenceContractEvaluator,
    EvidenceItem,
    product_contract,
    training_contract,
    VALID, ABSENT, STALE, INVALID, CONTRADICTORY, UNVERIFIABLE, REVOKED,
)
from app.hardening.runtime import HarnessClock

NOW = datetime(2026, 9, 11, 12, 0, tzinfo=timezone.utc)


def evaluator():
    return EvidenceContractEvaluator(HarnessClock(NOW))


def product_item(**changes):
    base = EvidenceItem(
        evidence_id="EV-PROD-1",
        control_id="HC.PRODUCT.VERSION.AUTHORISED",
        subject="AVT-001:1.0.0",
        asserted_state="AUTHORISED",
        evidence_source="DEPLOYMENT_REGISTRY",
        evidence_authority="DEPLOYMENT_REGISTRY",
        observed_at=NOW.isoformat(),
        provenance_reference="registry://deployment/AVT-001/1.0.0",
        deployment_context="ASVH-TEST-01",
        product_identifier="AVT-001",
        product_version="1.0.0",
        max_age_seconds=300,
    )
    return replace(base, **changes)


def training_item(**changes):
    base = EvidenceItem(
        evidence_id="EV-TRAIN-1",
        control_id="HC.CLINICIAN.TRAINING.CURRENT",
        subject="CLN-001",
        asserted_state="CURRENT",
        evidence_source="TRAINING_REGISTRY",
        evidence_authority="TRAINING_REGISTRY",
        observed_at=NOW.isoformat(),
        provenance_reference="training://CLN-001/ambient-scribing",
        max_age_seconds=86400,
    )
    return replace(base, **changes)


def eval_product(items, contract=None):
    return evaluator().evaluate(
        contract or product_contract(), items,
        expected_subject="AVT-001:1.0.0",
        expected_deployment="ASVH-TEST-01",
        expected_product_identifier="AVT-001",
        expected_product_version="1.0.0",
        requester_source="REQUESTING_AI",
    )


def test_h4_001_valid_authoritative_evidence():
    r = eval_product([product_item()]); assert r.status == VALID and r.outcome == "ALLOW"

def test_h4_002_missing_required_evidence():
    r = eval_product([]); assert r.status == ABSENT and r.outcome == "REFUSE"

def test_h4_003_stale_evidence():
    old = (NOW - timedelta(seconds=301)).isoformat(); r = eval_product([product_item(observed_at=old)])
    assert r.status == STALE and r.outcome == "REFUSE"

def test_h4_004_revoked_evidence():
    r = eval_product([product_item(revoked=True)]); assert r.status == REVOKED and r.outcome == "REFUSE"

def test_h4_005_unknown_authority():
    r = eval_product([product_item(evidence_source="UNKNOWN", evidence_authority="UNKNOWN")])
    assert r.status == UNVERIFIABLE and r.outcome == "REFUSE"

def test_h4_006_requester_self_attestation_rejected():
    r = eval_product([product_item(evidence_source="REQUESTING_AI", evidence_authority="REQUESTING_AI")])
    assert r.status == UNVERIFIABLE

def test_h4_007_wrong_subject():
    r = eval_product([product_item(subject="AVT-OTHER:1.0.0")]); assert r.status == INVALID

def test_h4_008_wrong_deployment():
    r = eval_product([product_item(deployment_context="OTHER")]); assert r.status == INVALID

def test_h4_009_wrong_product_version():
    r = eval_product([product_item(product_version="2.0.0")]); assert r.status == INVALID

def test_h4_010_non_permitted_source_same_value():
    r = eval_product([product_item(evidence_source="OTHER_REGISTRY", evidence_authority="OTHER_REGISTRY")])
    assert r.status == UNVERIFIABLE

def test_h4_011_conflicting_permitted_evidence():
    a = product_item(evidence_id="A", asserted_state="AUTHORISED")
    b = product_item(evidence_id="B", asserted_state="SUSPENDED")
    r = eval_product([a,b]); assert r.status == CONTRADICTORY and r.outcome == "REFUSE"

def test_h4_012_not_yet_valid():
    future = (NOW + timedelta(seconds=30)).isoformat(); r = eval_product([product_item(valid_from=future)])
    assert r.status == INVALID

def test_h4_013_missing_provenance():
    r = eval_product([product_item(provenance_reference=None)]); assert r.status == INVALID

def test_h4_014_integrity_failure():
    r = eval_product([product_item(integrity_valid=False)]); assert r.status == INVALID

def test_h4_015_valid_product_and_training_deterministic_aggregate():
    p = eval_product([product_item()])
    t = evaluator().evaluate(training_contract(), [training_item()], expected_subject="CLN-001")
    aggregate = "ALLOW" if p.outcome == "ALLOW" and t.outcome == "ALLOW" else "ESCALATE" if "ESCALATE" in {p.outcome,t.outcome} else "REFUSE"
    assert p.status == VALID and t.status == VALID and aggregate == "ALLOW"

def test_h4_016_stale_training_not_masked():
    p = eval_product([product_item()])
    old = (NOW - timedelta(days=2)).isoformat()
    t = evaluator().evaluate(training_contract(), [training_item(observed_at=old)], expected_subject="CLN-001")
    assert p.status == VALID and t.status == STALE and t.outcome == "ESCALATE"

def test_h4_017_deterministic_same_inputs():
    a = eval_product([product_item()]); b = eval_product([product_item()]); assert a == b

def test_h4_018_mutation_requires_fresh_evaluation():
    original = eval_product([product_item()])
    changed = eval_product([product_item(asserted_state="SUSPENDED")])
    assert original.status == VALID and changed.status == INVALID and original != changed

def test_h4_019_contract_version_change_not_same_result_identity():
    a = eval_product([product_item()], product_contract("CC-1.0"))
    b = eval_product([product_item()], product_contract("CC-2.0"))
    assert a.contract_version != b.contract_version

def test_h4_020_reconstruction_fields_present():
    r = eval_product([product_item()])
    assert r.control_id and r.evidence_ids == ("EV-PROD-1",) and r.evidence_sources == ("DEPLOYMENT_REGISTRY",)
    assert r.evidence_authorities == ("DEPLOYMENT_REGISTRY",) and r.provenance_references[0] and r.predicate_result is True
