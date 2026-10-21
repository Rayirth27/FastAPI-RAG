# FastAPI RAG Engine

A modular, security-focused Retrieval-Augmented Generation (RAG) backend, built with Python, FastAPI, PostgreSQL, and pgvector.
The project aims to provide secure document ingestion, vector-based semantic retrieval, and grounded LLM-generated answers with source citations.

### Project Status: Actively Under Development

The current implementation supports document persistence in PostgreSQL, SQLAlchemy ORM integration, and API-key authentication. The complete RAG pipeline is being developed incrementally.

## Architecture & Stack

* **API Framework:** FastAPI with Pydantic request/response validation
* **Database:** PostgreSQL 17 with pgvector
* **Database Access:** SQLAlchemy 2.x and psycopg 3
* **Authentication:** API-key authentication using the X-API-Key header
* **Infrastructure:** Docker Compose
* **Testing:** pytest and FastAPI TestClient

## Key Features

* **Zero API Costs:** Built entirely on open-source embedding models and local LLM runtimes—no paid API keys required.
* **Data Privacy:** Runs 100% locally or on self-hosted infra, ensuring sensitive document content never leaves your environment.
* **Data Validation:** Strict JSON contracts via Pydantic (`QuestionRequest`, `AnswerResponse`, `Document`).
* **Document Persistence:** Direct integration with PostgreSQL for persistent document and vector chunk storage.
* **Semantic Search:** Fast cosine similarity vector queries using `pgvector`.
* **Zero Hallucination Focus:** Returns strict source citations (`sources: list[str]`) along with generated responses.
* **Observability & Reliability:** Edge error handling, query latency logging, and comprehensive test coverage.