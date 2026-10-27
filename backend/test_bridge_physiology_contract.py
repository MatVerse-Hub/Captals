"""Contract tests for the read-only Bridge physiology projection (P0).

Fixture mirrors the app/captals_physiology_projection.py output in Bridge PR
#109. Independent service identity and replay verification remain HOLD.
"""
from fastapi import FastAPI
from fastapi.testclient import TestClient
from routes.captals import router

app = FastAPI()
app.include_router(router, prefix="/api/captals")
client = TestClient(app)


def projected(**changes):
    body = {
        "event_id": "c" * 64,
        "track_id": "cycle:" + "c" * 64,
        "source": "bridge.physiology.simulated",
        "gate_decision": "PASS",
        "evidence_status": "UNVERIFIED",
        "replay_status": "NOT_AVAILABLE",
        "capital_delta": {},
        "costs": {"computational": {
            "value": 0.001,
            "unit": "cpu_second",
            "instrument": "deterministic_lab.logical_cpu",
        }},
        "budget_limits": {},
        "provenance_ref": "physiology:" + "c" * 64 + ":memory",
        "receipt_ref": "d" * 64,
        "legacy_omega_score": None,
    }
    body.update(changes)
    return body


def test_bridge_projection_is_schema_compatible_but_not_eligible():
    response = client.post("/api/captals/evaluate", json=projected())
    assert response.status_code == 200
    output = response.json()
    assert output["event_id"] == "c" * 64
    assert output["state"] == "NEUTRAL"
    assert output["allocation_status"] == "HOLD"
    assert output["authorization_implication"] == "NONE"
    assert "evidence_not_verified" in output["reasons"]


def test_no_proposal_hold_is_never_eligible():
    response = client.post("/api/captals/evaluate", json=projected(
        gate_decision="HOLD", costs={}
    ))
    assert response.status_code == 200
    assert response.json()["allocation_status"] == "HOLD"
    assert response.json()["authorization_implication"] == "NONE"


def test_external_block_cannot_be_promoted():
    response = client.post("/api/captals/evaluate", json=projected(
        gate_decision="BLOCK"
    ))
    assert response.status_code == 200
    assert response.json()["allocation_status"] == "INELIGIBLE"
    assert response.json()["authorization_implication"] == "NONE"


def test_synthetic_positive_capital_cannot_override_unverified_status():
    response = client.post("/api/captals/evaluate", json=projected(
        capital_delta={"scientific": {"value": 1, "unit": "milestone",
                                      "instrument": "synthetic_lab"}}
    ))
    assert response.status_code == 200
    assert response.json()["state"] == "ACCUMULATING"
    assert response.json()["allocation_status"] == "HOLD"


def test_negative_resource_cost_rejected():
    response = client.post("/api/captals/evaluate", json=projected(
        costs={"computational": {"value": -9, "unit": "cpu_second",
                                  "instrument": "deterministic_lab.logical_cpu"}}
    ))
    assert response.status_code == 422


def test_missing_measurement_instrument_rejected():
    response = client.post("/api/captals/evaluate", json=projected(
        costs={"computational": {"value": 0.1, "unit": "cpu_second",
                                  "instrument": ""}}
    ))
    assert response.status_code == 422


def test_budget_violation_fails_closed_when_supplied():
    response = client.post("/api/captals/evaluate", json=projected(
        evidence_status="VERIFIED",
        replay_status="EXACT_MATCH",
        capital_delta={"technological": {"value": 1, "unit": "capability",
                                         "instrument": "capability_registry"}},
        budget_limits={"computational": {"max_value": 0.0005,
                                           "unit": "cpu_second"}}
    ))
    assert response.status_code == 200
    result = response.json()
    assert result["allocation_status"] == "INELIGIBLE"
    assert result["authorization_implication"] == "NONE"


def test_legacy_omega_does_not_authorize_even_if_high():
    response = client.post("/api/captals/evaluate", json=projected(
        legacy_omega_score=9000.0
    ))
    assert response.status_code == 200
    result = response.json()
    assert result["allocation_status"] == "HOLD"
    assert result["authorization_implication"] == "NONE"
