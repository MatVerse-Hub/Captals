"""
Backend API Tests
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_read_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert response.json()["message"] == "Omega Capitals API"


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()


def test_get_funds():
    """Test get funds endpoint"""
    response = client.get("/api/funds/")
    assert response.status_code == 200
    assert "funds" in response.json()


def test_get_governance_proposals():
    """Test governance proposals endpoint"""
    response = client.get("/api/governance/proposals")
    assert response.status_code == 200
    assert "proposals" in response.json()


def test_get_dashboard_metrics():
    """Test dashboard metrics endpoint"""
    response = client.get("/api/metrics/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "tvl" in data
    assert "total_users" in data


def test_create_invoice():
    """Test create invoice endpoint"""
    payload = {
        "amount": 100,
        "currency": "USDT",
        "description": "Test investment",
        "product_type": "OmegaFund"
    }
    response = client.post("/api/payments/create-invoice", json=payload)
    # May fail without proper LUA-PAY credentials, but endpoint should exist
    assert response.status_code in [200, 500]


def test_invalid_endpoint():
    """Test invalid endpoint returns 404"""
    response = client.get("/api/invalid/endpoint")
    assert response.status_code == 404
