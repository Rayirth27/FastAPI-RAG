from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import HTTPException # Add error handling

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

@app.post("/ingest")
def ingest(doc:Document):
    documents.append({"title": doc.title, "content": doc.content})
    return {"message":f"Ingested: {doc.title}", "total_docs":len(documents)}


@app.get("/documents")
def list_documents():
    return {"count": len(documents), "titles": [d["title"] for d in documents]}