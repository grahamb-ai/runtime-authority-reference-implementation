## @file test_api.py
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Integration tests: the full HTTP API against an in-memory SQLite database.
#
"""Integration tests for the API endpoints.

These drive the real FastAPI app through 'TestClient', but override the
database dependency with an in-memory SQLite engine so the suite runs with no
PostgreSQL server. Only the test session is swapped; production still uses
PostgreSQL via 'DATABASE_URL'.
"""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.database import get_session
from main import app

FIXTURE = Path(__file__).parent / "fixtures" / "sample-policy.txt"


@pytest.fixture(name="client")
## @fn client_fixture()
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Pytest fixture providing a TestClient wired to an in-memory SQLite database.
#
def client_fixture():
    """Provide a TestClient backed by a fresh in-memory SQLite database.

    'StaticPool' + a shared connection keeps the in-memory DB alive for the
    whole test, and 'dependency_overrides' redirects 'get_session' to it.
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    ## @fn override_get_session()
    #  @author FlowSignal Dev Team
    #  @version 0.1
    #  @date 25 July 2026
    #  @brief FastAPI dependency override routing the app to the in-memory test database instead of the real one.
    #
    def override_get_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()  # isolate each test

## @fn _upload_policy(client)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test helper that uploads the fixture policy through the real API before a test runs.
#  @param client See test body for how this fixture/argument is used.
#
def _upload_policy(client):
    """Upload the sample policy fixture through the API."""
    with open(FIXTURE, "rb") as fh:
        return client.post(
            "/api/v1/specs/upload",
            files={"file": ("sample-policy.txt", fh, "text/plain")},
        )

## @fn _envelope(role, amount, evidence)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test helper that builds a request envelope dict with sensible defaults for the scenario under test.
#  @param role See test body for how this fixture/argument is used.
#  @param amount See test body for how this fixture/argument is used.
#  @param evidence See test body for how this fixture/argument is used.
#
def _envelope(role, amount, evidence):
    """Build a payment.release request body."""
    return {
        "action": "payment.release",
        "target": "SAP_PAYMENT_RELEASE",
        "requester": {"id": "u1", "role": role},
        "context": {"amount": amount, "currency": "EUR"},
        "evidence": evidence,
    }


## @fn test_health(client)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test: Health.
#  @param client See test body for how this fixture/argument is used.
#
def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

## @fn test_upload_extracts_rules(client)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test: Upload extracts rules.
#  @param client See test body for how this fixture/argument is used.
#
def test_upload_extracts_rules(client):
    r = _upload_policy(client)
    assert r.status_code == 200
    body = r.json()
    assert body["authority_rules"] == 5
    assert body["admissibility_rules"] == 1
    assert body["total_rules"] == 6


## @fn test_upload_rejects_unsupported_type(client)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test: Upload rejects unsupported type.
#  @param client See test body for how this fixture/argument is used.
#
def test_upload_rejects_unsupported_type(client):
    r = client.post(
        "/api/v1/specs/upload",
        files={"file": ("policy.exe", b"nope", "application/octet-stream")},
    )
    assert r.status_code == 400


## @fn test_evaluate_allow(client)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test: Evaluate allow.
#  @param client See test body for how this fixture/argument is used.
#
def test_evaluate_allow(client):
    _upload_policy(client)
    r = client.post("/api/v1/orders/evaluate", json=_envelope("regional_manager", 40000, ["invoice"]))
    assert r.status_code == 200
    assert r.json()["decision"] == "ALLOW"


## @fn test_evaluate_escalate_over_limit(client)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test: Evaluate escalate over limit.
#  @param client See test body for how this fixture/argument is used.
#
def test_evaluate_escalate_over_limit(client):
    _upload_policy(client)
    r = client.post(
        "/api/v1/orders/evaluate",
        json=_envelope("regional_manager", 250000, ["invoice", "purchase_order"]),
    )
    assert r.json()["decision"] == "ESCALATE"

## @fn test_evaluate_refuse_bad_role(client)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test: Evaluate refuse bad role.
#  @param client See test body for how this fixture/argument is used.
#
def test_evaluate_refuse_bad_role(client):
    _upload_policy(client)
    r = client.post("/api/v1/orders/evaluate", json=_envelope("intern", 10000, []))
    body = r.json()
    assert body["decision"] == "REFUSE"
    assert body["required_action"] is None

## @fn test_assess_does_not_persist(client)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test: Assess does not persist.
#  @param client See test body for how this fixture/argument is used.
#
def test_assess_does_not_persist(client):
    # /assess returns a record but must not store it -> not retrievable afterwards.
    _upload_policy(client)
    r = client.post("/api/v1/orders/assess", json=_envelope("regional_manager", 40000, ["invoice"]))
    assert r.status_code == 200
    record_id = r.json()["id"]
    assert client.get(f"/api/v1/orders/{record_id}").status_code == 404

## @fn test_get_record_after_evaluate(client)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test: Get record after evaluate.
#  @param client See test body for how this fixture/argument is used.
#
def test_get_record_after_evaluate(client):
    # /evaluate persists, so the record can be fetched by id.
    _upload_policy(client)
    r1 = client.post("/api/v1/orders/evaluate", json=_envelope("regional_manager", 40000, ["invoice"]))
    record_id = r1.json()["id"]
    r2 = client.get(f"/api/v1/orders/{record_id}")
    assert r2.status_code == 200
    assert r2.json()["id"] == record_id

## @fn test_get_unknown_record_404(client)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Test: Get unknown record 404.
#  @param client See test body for how this fixture/argument is used.
#
def test_get_unknown_record_404(client):
    assert client.get("/api/v1/orders/does-not-exist").status_code == 404
