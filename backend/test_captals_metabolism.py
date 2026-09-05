"""Tests for the Captals metabolism fusion layer."""

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def _base_payload():
    return {
        "event_id": "EVT-001",
        "track_id": "TRAIL-001",
        "milestone_id": "MILESTONE-001",
        "m_bit_ref": "MBIT-001",
        "source": "urano_experiment",
        "gate_decision": "PASS",
        "evidence_status": "VERIFIED",
        "replay_status": "EXACT_MATCH",
        "capital_delta": {
            "scientific": {
                "value": 1.0,
                "unit": "validated_milestone",
                "instrument": "evidence_pack_validator"
            },
            "technological": {
                "value": 1.0,
                "unit": "capability",
                "instrument": "capability_registry"
            }
        },
        "costs": {
            "computational": {
                "value": 8.0,
                "unit": "cpu_hour",
                "instrument": "runtime_meter"
            }
        },
        "budget_limits": {
            "computational": {
                "max_value": 10.0,
                "unit": "cpu_hour"
            }
        },
        "provenance_ref": "prov:001",
        "receipt_ref": "receipt:001"
    }


def test_schema_keeps_dimensions_separate():
    response = client.get("/api/captals/schema")
    assert response.status_code == 200
    payload = response.json()
    assert payload["canonical_name"] == "Captals"
    assert payload["legacy_surface"] == "Omega Capitals (Ω-Capitals)"
    assert "scientific" in payload["capital_dimensions"]
    assert "risk" in payload["cost_dimensions"]
    assert "trust != value != price != capital" in payload["invariants"]


def test_admissible_accumulation_is_eligible():
    response = client.post("/api/captals/evaluate", json=_base_payload())
    assert response.status_code == 200
    payload = response.json()
    assert payload["state"] == "ACCUMULATING"
    assert payload["allocation_status"] == "ELIGIBLE"
    assert "scientific" in payload["positive_capitals"]


def test_external_block_is_never_overridden_by_value():
    payload = _base_payload()
    payload["gate_decision"] = "BLOCK"
    payload["capital_delta"]["financial"] = {
        "value": 1000000,
        "unit": "BRL",
        "instrument": "audited_ledger"
    }
    response = client.post("/api/captals/evaluate", json=payload)
    assert response.status_code == 200
    result = response.json()
    assert result["allocation_status"] == "INELIGIBLE"
    assert "external_gate_block" in result["reasons"]


def test_unverified_evidence_holds_allocation():
    payload = _base_payload()
    payload["evidence_status"] = "UNVERIFIED"
    response = client.post("/api/captals/evaluate", json=payload)
    assert response.status_code == 200
    assert response.json()["allocation_status"] == "HOLD"


def test_budget_violation_is_ineligible_without_scalar_score():
    payload = _base_payload()
    payload["costs"]["computational"]["value"] = 11.0
    response = client.post("/api/captals/evaluate", json=payload)
    assert response.status_code == 200
    result = response.json()
    assert result["allocation_status"] == "INELIGIBLE"
    assert result["budget_violations"][0]["dimension"] == "computational"


def test_mixed_capital_change_is_tradeoff_and_holds_without_policy():
    payload = _base_payload()
    payload["capital_delta"]["relational"] = {
        "value": -1.0,
        "unit": "validated_relation",
        "instrument": "relation_integrity_registry"
    }
    response = client.post("/api/captals/evaluate", json=payload)
    assert response.status_code == 200
    result = response.json()
    assert result["state"] == "TRADEOFF"
    assert result["allocation_status"] == "HOLD"
    assert "cross_dimension_tradeoff_requires_explicit_policy" in result["reasons"]
    assert "relational" in result["negative_capitals"]


def test_legacy_omega_is_context_not_authorization():
    response = client.post(
        "/api/captals/legacy/omega",
        json={
            "omega_score": 9200,
            "tvl": 4700000,
            "volume_24h": 450000,
            "apr": 12.5,
            "asset_or_pool": "Omega Stable Fund"
        }
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["classification"] == "LEGACY_MARKET_SIGNAL"
    assert payload["trust_implication"] == "NONE"
    assert payload["authorization_implication"] == "NONE"
    assert "explicit_gate_decision" in payload["requires_for_allocation"]


def test_budget_unit_mismatch_is_rejected():
    payload = _base_payload()
    payload["budget_limits"]["computational"]["unit"] = "joule"
    response = client.post("/api/captals/evaluate", json=payload)
    assert response.status_code == 422


def test_infinite_budget_limit_is_rejected():
    payload = _base_payload()
    payload["budget_limits"]["computational"]["max_value"] = "Infinity"
    response = client.post("/api/captals/evaluate", json=payload)
    assert response.status_code == 422
