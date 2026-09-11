from dataclasses import replace
from datetime import datetime, timedelta, timezone

from app.hardening.evidence_contract import (
    EvidenceContractEvaluator,
    EvidenceItem,
    product_contract,
    INVALID,
)
from app.hardening.runtime import HarnessClock

NOW = datetime(2026, 9, 11, 12, 0, tzinfo=timezone.utc)


def evaluator():
    return EvidenceContractEvaluator(HarnessClock(NOW))


def item(**changes):
    base = EvidenceItem(
        evidence_id="EV-HOSTILE-1",
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


def evaluate(items):
    return evaluator().evaluate(
        product_contract(),
        items,
        expected_subject="AVT-001:1.0.0",
        expected_deployment="ASVH-TEST-01",
        expected_product_identifier="AVT-001",
        expected_product_version="1.0.0",
        requester_source="REQUESTING_AI",
    )


def test_hostile_future_observed_at_cannot_be_current_evidence():
    future = (NOW + timedelta(minutes=10)).isoformat()
    result = evaluate([item(observed_at=future)])
    assert result.status == INVALID
    assert result.outcome == "REFUSE"


def test_hostile_malformed_timestamp_fails_explicitly_not_by_exception():
    result = evaluate([item(observed_at="not-an-iso-timestamp")])
    assert result.status == INVALID
    assert result.outcome == "REFUSE"


def test_hostile_duplicate_evidence_identity_collision_is_not_valid():
    first = item(
        evidence_id="EV-COLLISION",
        provenance_reference="registry://deployment/source-record-A",
    )
    second = item(
        evidence_id="EV-COLLISION",
        provenance_reference="registry://deployment/source-record-B",
    )
    result = evaluate([first, second])
    assert result.status == INVALID
    assert result.outcome == "REFUSE"


def test_hostile_same_id_same_payload_duplicate_is_not_silently_counted_twice():
    same = item(evidence_id="EV-DUPLICATE")
    result = evaluate([same, same])
    # Duplicate transport delivery must be de-duplicated rather than becoming
    # two independent pieces of authority evidence.
    assert result.evidence_ids == ("EV-DUPLICATE",)
