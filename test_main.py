from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health():
    response = client.get("/")
    assert response.status_code == 200

def test_ask_empty_question():
    response = client.post("/ask", json={"question":" "})
    assert response.status_code == 400

def test_ingest_document():
    response = client.post("/ingest", json={"title":"Test","content":"Hello To this World"})
    assert response.status_code == 200
    assert response.json()["total_docs"] == 1
