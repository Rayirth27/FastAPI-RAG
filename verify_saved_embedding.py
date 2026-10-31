from database import SessionLocal
from models import DocumentRecord, DocumentChunkRecord


CHUNK_ID = 1
EXPECTED_DOCUMENT_ID = 3
EXPECTED_MODEL = "embeddinggemma:latest"


with SessionLocal() as session:

    # Fetch the saved chunk using its primary key
    chunk = session.get(DocumentChunkRecord, CHUNK_ID)

    if chunk is None:
        raise RuntimeError("Chunk not found!")

    # Fetch the associated document
    document = session.get(
        DocumentRecord,
        chunk.document_id,
    )

    if document is None:
        raise RuntimeError("Parent document not found!")

    # Validate stored values
    assert chunk.document_id == EXPECTED_DOCUMENT_ID
    assert chunk.embedding_model == EXPECTED_MODEL
    assert len(chunk.embedding) == 768
    assert chunk.chunk_index == 0
    assert chunk.content == document.content

    print("Database retrieval successful!")
    print(f"Document ID: {document.id}")
    print(f"Document Title: {document.title}")
    print(f"Chunk ID: {chunk.id}")
    print(f"Chunk Index: {chunk.chunk_index}")
    print(f"Chunk Content: {chunk.content}")
    print(f"Embedding Model: {chunk.embedding_model}")
    print(f"Embedding Dimensions: {len(chunk.embedding)}")
    print(f"First 5 Values: {chunk.embedding[:5]}")