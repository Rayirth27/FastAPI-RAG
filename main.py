
from fastapi import Depends, FastAPI, HTTPException, File, UploadFile
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models import DocumentRecord

from security import require_api_key

from typing import Annotated
from pydantic import StringConstraints

app = FastAPI()


class QuestionRequest(BaseModel):
    question: str
    top_k: int = 3


class AnswerResponse(BaseModel):
    question: str
    answer: str
    sources: list[str]


class Document(BaseModel):
    title: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
            min_length=1,
            max_length=200,
        ),
    ]

    content: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
            min_length=1,
            max_length=20000,
        ),
    ]



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

MAX_PDF_SIZE = 5 * 1024 * 1024 # 5 MB

@app.post("/upload", dependencies=[Depends(require_api_key)])
async def upload_pdf(file: UploadFile = File(...)):
    try:
        # TO check the declated content type
        if file.content_type != "application/pdf":
            raise HTTPException(
                status_code=415,
                detail="Only PDF files are allowed",
            )

        #2. Read at most one byte beyond the allowed limit
        content = await file.read(MAX_PDF_SIZE + 1)

        if len(content) > MAX_PDF_SIZE:
            raise HTTPException(
                status_code=413,
                detail="PDF exeeds 5 MB limit",
            )

        #3. Check the PDF file signature
        if not content.startswith(b"%PDF-"):
            raise HTTPException(
                status_code=422,
                detail="Invalid PDF file"
            )
        
        return{
            "message": "PDF accepted for processing",
            "size_bytes": len(content)
        }

    finally:
        await file.close()