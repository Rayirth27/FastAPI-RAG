from sqlalchemy import select

from database import SessionLocal
from models import DocumentChunkRecord, DocumentRecord
from embeddings import generate_embedding, EMBEDDING_MODEL


QUESTION = "How do employees log into company applications?"
TOP_K = 5


def main():
    # 1. Convert the question to a vector.
    query_vector = generate_embedding(QUESTION)

    print(f"Question: {QUESTION}")
    print(f"Embedding dimensions: {len(query_vector)}")

    # 2. Define cosine distance between query and stored vectors.
    distance = (
        DocumentChunkRecord.embedding
        .cosine_distance(query_vector)
        .label("distance")
    )

    # 3. Retrieve nearest chunks with document provenance.
    statement = (
        select(
            DocumentChunkRecord.id,
            DocumentChunkRecord.document_id,
            DocumentRecord.title,
            DocumentChunkRecord.content,
            distance,
        )
        .join(
            DocumentRecord,
            DocumentChunkRecord.document_id == DocumentRecord.id,
        )
        .where(DocumentChunkRecord.embedding_model == EMBEDDING_MODEL)
        .order_by(distance.asc(), DocumentChunkRecord.id.asc())
        .limit(TOP_K)
    )

    # 4. Execute against PostgreSQL.
    with SessionLocal() as session:
        results = session.execute(statement).all()

    # 5. Display the actual measured distances.
    print(f"Results found: {len(results)}")

    for rank, row in enumerate(results, start=1):
        print(f"\nRank: {rank}")
        print(f"Chunk ID: {row.id}")
        print(f"Document ID: {row.document_id}")
        print(f"Title: {row.title}")
        print(f"Content: {row.content}")
        print(f"Cosine distance: {row.distance:.6f}")


if __name__ == "__main__":
    main()
