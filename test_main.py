from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_receive_lead_success():
    payload = {
        "name": "Priscila Teste",
        "email": "priscila@testcorp.com",
        "company": "TestCorp S.A.",
    }
    response = client.post("/webhook/leads", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "is_hot" in data


def test_receive_lead_invalid_email():
    payload = {
        "name": "Lead Inválido",
        "email": "email-invalido-sem-formato",
        "company": "BadData",
    }
    response = client.post("/webhook/leads", json=payload)
    assert response.status_code == 422