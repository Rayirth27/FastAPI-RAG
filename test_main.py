from fastapi.testclient import TestClient
from main import app
from unittest.mock import MagicMock
import main

import pytest

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


@pytest.mark.parametrize(
    "payload",
    [
        {"title": "   ", "content": ""},
        {"title": "A" * 201, "content": "Valid content"},
        {"title": "Valid title", "content": "A" * 20001},
    ],
)
def test_ingest_rejects_invalid_documents(monkeypatch, payload):
    monkeypatch.setenv("API_KEY", "test-only-api-key")

    fake_db = MagicMock()
    app.dependency_overrides[main.get_db] = lambda: fake_db

    try:
        response = client.post(
            "/ingest",
            json=payload,
            headers={"X-API-Key": "test-only-api-key"},
        )

        assert response.status_code == 422
        fake_db.add.assert_not_called()
        fake_db.commit.assert_not_called()

    finally:
        app.dependency_overrides.pop(main.get_db, None)



def test_upload_requires_api_key(monkeypatch):
    monkeypatch.setenv("API_KEY", "test-only-api-key")

    response = client.post(
        "/upload",
        files={
            "file": ("test.pdf", b"%PDF-1.4\n", "application/pdf")
        },
    )

    assert response.status_code == 401


def test_upload_rejects_non_pdf(monkeypatch):
    monkeypatch.setenv("API_KEY", "test-only-api-key")

    response = client.post(
        "/upload",
        headers={"X-API-Key": "test-only-api-key"},
        files={
            "file": ("test.txt", b"Hello world", "text/plain")
        },
    )

    assert response.status_code == 415


def test_upload_rejects_fake_pdf(monkeypatch):
    monkeypatch.setenv("API_KEY", "test-only-api-key")

    response = client.post(
        "/upload",
        headers={"X-API-Key": "test-only-api-key"},
        files={
            "file": (
                "fake.pdf",
                b"This is not a PDF",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 422


def test_upload_rejects_oversized_pdf(monkeypatch):
    monkeypatch.setenv("API_KEY", "test-only-api-key")

    oversized_content = b"%PDF-" + b"A" * (5 * 1024 * 1024)

    response = client.post(
        "/upload",
        headers={"X-API-Key": "test-only-api-key"},
        files={
            "file": (
                "large.pdf",
                oversized_content,
                "application/pdf",
            )
        },
    )

    assert response.status_code == 413



def test_upload_accepts_valid_pdf(monkeypatch):
    from io import BytesIO
    from reportlab.pdfgen import canvas

    monkeypatch.setenv("API_KEY", "test-only-api-key")

    buffer = BytesIO()

    pdf = canvas.Canvas(buffer)
    pdf.drawString(
        72, 750,
        "FastAPI RAG PDF integration test"
    )
    pdf.save()

    pdf_content = buffer.getvalue()

    response = client.post(
        "/upload",
        headers={"X-API-Key": "test-only-api-key"},
        files={
            "file": (
                "sample.pdf",
                pdf_content,
                "application/pdf",
            )
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert result["message"] == "PDF text extracted successfully"
    assert result["size_bytes"] == len(pdf_content)
    assert "FastAPI RAG PDF integration test" in result["extracted_text"]
    assert result["character_count"] > 0
