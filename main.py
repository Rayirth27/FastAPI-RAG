from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import HTTPException # Add error handling

import os
import psycopg2


class QuestionRequest(BaseModel):
    question: str
    top_k: int = 3 # how many documents chunks to retrieve

class AnswerResponse(BaseModel):
    question: str
    answer: str
    sources: list[str]

app = FastAPI()

@app.get("/")
def health():
    return {"status":"ok"}

@app.post("/ask", response_model = AnswerResponse)
def ask(request: QuestionRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty") # Add error handling
    return AnswerResponse( 
        question=request.question,
        answer="not implemented yet",
        sources=[]
    )

documents = []  #in-memory for now

class Document(BaseModel):
    title: str
    content: str     

def get_db():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

@app.post("/ingest")
def ingest(doc:Document):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO documents (title, content) VALUES (%s, %s)",
        (doc.title, doc.content)
    )
    conn.commit()
    cur.close()
    conn.close()
    return {"message":f"Ingested: {doc.title}"}


@app.get("/documents")
def list_documents():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, title FROM documents ORDER BY created_at DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {
        "count": len(rows),
        "documents": [{"id": r[0], "title": r[1]} for r in rows]
    }