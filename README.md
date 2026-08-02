# FastAPI RAG Engine

A production-ready Modular Monolith API for **Retrieval-Augmented Generation (RAG)** built with Python, FastAPI and PostgresSQL.

This API allows clients to ingest enterprise documents, automatically chunk and embed text into a vector space, perform similarity searches, and generate grounded answers via LLMs—complete with source citations.

## Architecture & Stack

* **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Asynchronous Web API & Pydantic Schemas)
* **LLM Engine:** Local Open-Source LLM (e.g., [Ollama](https://ollama.com/) / Hugging Face Transformers)
* **Database & Vector Search:** PostgreSQL + [`pgvector`](https://github.com/pgvector/pgvector)
* **Embeddings:** `sentence-transformers` (`all-MiniLM-L6-v2` - free & local)
* **Testing:** `pytest` & FastAPI `TestClient`
* **Infrastructure:** Docker, GitHub Actions (CI/CD)

## Key Features

* **Zero API Costs:** Built entirely on open-source embedding models and local LLM runtimes—no paid API keys required.
* **Data Privacy:** Runs 100% locally or on self-hosted infra, ensuring sensitive document content never leaves your environment.
* **Data Validation:** Strict JSON contracts via Pydantic (`QuestionRequest`, `AnswerResponse`, `Document`).
* **Document Persistence:** Direct integration with PostgreSQL for persistent document and vector chunk storage.
* **Semantic Search:** Fast cosine similarity vector queries using `pgvector`.
* **Zero Hallucination Focus:** Returns strict source citations (`sources: list[str]`) along with generated responses.
* **Observability & Reliability:** Edge error handling, query latency logging, and comprehensive test coverage.
