from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def health():
    return {"status":"ok"}

@app.post("/ask")
def ask(question: str):
    return {"question": question, "answer":"not implemented yet"}
