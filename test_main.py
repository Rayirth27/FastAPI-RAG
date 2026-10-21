from fastapi.testclient import TestClient
from main import app
from unittest.mock import MagicMock
import main

client = TestClient(app)

def test_health():
    response = client.get("/")
    assert response.status_code == 200

def test_ask_empty_question(monkeypatch):
    monkeypatch.setenv("API_KEY", "test-only-api-key")

    response = client.post(
        "/ask",
        json={"question": " "},
        headers={"X-API-Key": "test-only-api-key"},
    )

    assert response.status_code == 400


def test_ingest_document(monkeypatch):
    monkeypatch.setenv("API_KEY", "test-only-api-key")

    fake_db = MagicMock()
    app.dependency_overrides[main.get_db] = lambda: fake_db

    try:
        response = client.post(
            "/ingest",
            json={
                "title": "Test",
                "content": "Hello To this World",
            },
            headers={"X-API-Key": "test-only-api-key"},
        )

        assert response.status_code == 200
        assert response.json() == {"message": "Ingested: Test"}

        fake_db.add.assert_called_once()
        fake_db.commit.assert_called_once()

    finally:
        app.dependency_overrides.clear()

def test_ingest_requires_api_key():
    response = client.post(
        "/ingest",
        json={
            "title": "Unauthorized Test",
            "content": "This must not be inserted",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing API key"

def test_ingest_rejects_invalid_api_key(monkeypatch):
    monkeypatch.setenv("API_KEY", "correct-test-key")

    response = client.post(
        "/ingest",
        json={
            "title": "Unauthorized",
            "content": "Should not be inserted",
        },
        headers={"X-API-Key": "wrong-test-key"},
    )

    assert response.status_code == 401
    