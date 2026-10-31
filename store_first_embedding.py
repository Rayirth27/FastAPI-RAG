import json
import math
from urllib.request import Request, urlopen

from database import SessionLocal
from models import DocumentRecord, DocumentChunkRecord


TEXT = "Employees must authenticate using single sign-on."
MODEL = "embeddinggemma:latest"

OLLAMA_URL = "http://127.0.0.1:11434/api/embed"


# STEP 1: Prepare the Ollama API request
payload = {
    "model": MODEL,
    "input": TEXT,
}

request = Request(
    OLLAMA_URL,
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST",
)


# STEP 2: Generate an embedding
with urlopen(request, timeout=120) as response:
    result = json.load(response)

vectors = result.get("embeddings", [])

if len(vectors) != 1:
    raise ValueError("Expected exactly one embedding")

embedding = vectors[0]


# STEP 3: Validate the embedding
if len(embedding) != 768:
    raise ValueError(
        f"Expected 768 dimensions, got {len(embedding)}"
    )

if not all(
    isinstance(value, (int, float))
    and math.isfinite(value)
    for value in embedding
):
    raise ValueError("Embedding contains invalid values")

print("Embedding generated successfully!")
print(f"Dimensions: {len(embedding)}")


# STEP 4: Create document and chunk in one transaction
with SessionLocal() as session:

    with session.begin():

        document = DocumentRecord(
            title="Employee SSO Policy - Learning Experiment",
            content=TEXT,
        )

        session.add(document)

        # Send INSERT and obtain generated document ID
        session.flush()

        document_id = document.id

        chunk = DocumentChunkRecord(
            document_id=document_id,
            chunk_index=0,
            content=TEXT,
            embedding=embedding,
            embedding_model=MODEL,
        )

        session.add(chunk)

        # Obtain generated chunk ID
        session.flush()

        chunk_id = chunk.id


# Exiting session.begin() successfully commits.
print("Database transaction committed!")
print(f"Document ID: {document_id}")
print(f"Chunk ID: {chunk_id}")