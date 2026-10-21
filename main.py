
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models import DocumentRecord

from security import require_api_key

app = FastAPI()


class QuestionRequest(BaseModel):
    question: str
    top_k: int = 3


class AnswerResponse(BaseModel):
    question: str
    answer: str
    sources: list[str]


class Document(BaseModel):
    title: str
    content: str


@app.get("/")
def health():
    return {"status": "ok"}


@app.post(
    "/ask",
    response_model=AnswerResponse,
    dependencies=[Depends(require_api_key)]
)
def ask(request: QuestionRequest):
    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty",
        )

    return AnswerResponse(
        question=request.question,
        answer="not implemented yet",
        sources=[],
    )


@app.post("/ingest", dependencies=[Depends(require_api_key)])
def ingest(doc: Document, db: Session = Depends(get_db)):
    record = DocumentRecord(
        title=doc.title,
        content=doc.content,
    )

    db.add(record)
    db.commit()

    return {"message": f"Ingested: {doc.title}"}


@app.get("/documents", dependencies=[Depends(require_api_key)])
def list_documents(db: Session = Depends(get_db)):
    statement = select(DocumentRecord).order_by(
        DocumentRecord.created_at.desc()
    )

    records = db.scalars(statement).all()

    return {
        "count": len(records),
        "documents": [
            {"id": record.id, "title": record.title}
            for record in records
        ],
    }