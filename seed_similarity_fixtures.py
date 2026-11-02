from sqlalchemy import select

from database import SessionLocal
from models import DocumentRecord, DocumentChunkRecord
from embeddings import generate_embedding, EMBEDDING_MODEL


FIXTURES = [
    (
        "M8.13 Test - Access Management Policy",
        "Employees use the company's identity provider "
        "to sign in to internal applications.",
    ),
    (
        "M8.13 Test - SSO Setup Guide",
        "One login grants staff access to approved "
        "workplace applications through single sign-on.",
    ),
    (
        "M8.13 Test - Expense Reimbursement",
        "Employees submit travel expense reports "
        "before the fifth business day of each month.",
    ),
    (
        "M8.13 Test - Office Parking",
        "Parking permits are assigned every Monday "
        "at the facilities reception desk.",
    ),
]


def main():
    # Guard against accidentally duplicating test documents.
    titles = [title for title, _ in FIXTURES]

    with SessionLocal() as session:
        existing = session.scalars(
            select(DocumentRecord.title)
            .where(DocumentRecord.title.in_(titles))
        ).all()

    if existing:
        raise SystemExit(
            "M8.13 fixture titles already exist. "
            "No changes made. Inspect existing records "
            "before running this seed again."
        )

    # Generate embeddings before opening a write transaction.
    prepared = []

    for title, content in FIXTURES:
        embedding = generate_embedding(content)
        prepared.append((title, content, embedding))
        print(f"Prepared: {title} ({len(embedding)} dimensions)")

    # Store all four document/chunk pairs atomically.
    saved = []

    with SessionLocal() as session:
        with session.begin():
            for title, content, embedding in prepared:
                document = DocumentRecord(
                    title=title,
                    content=content,
                )
                session.add(document)
                session.flush()

                chunk = DocumentChunkRecord(
                    document_id=document.id,
                    chunk_index=0,
                    content=content,
                    embedding=embedding,
                    embedding_model=EMBEDDING_MODEL,
                )
                session.add(chunk)
                session.flush()

                saved.append((document.id, chunk.id, title))

    print("\nTransaction committed successfully.")

    for document_id, chunk_id, title in saved:
        print(f"Document {document_id} | Chunk {chunk_id} | {title}")


if __name__ == "__main__":
    main()