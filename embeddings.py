import math
import os

import httpx


OLLAMA_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://127.0.0.1:11434",
).rstrip("/")

EMBEDDING_MODEL = "embeddinggemma:latest"
EMBEDDING_DIMENSIONS = 768


class EmbeddingError(RuntimeError):
    pass


def generate_embedding(text: str) -> list[float]:
    if not text.strip():
        raise ValueError("Cannot embed empty text")

    try:
        response = httpx.post(
            f"{OLLAMA_URL}/api/embed",
            json={
                "model": EMBEDDING_MODEL,
                "input": text,
            },
            timeout=120.0,
        )

        response.raise_for_status()
        embedding = response.json()["embeddings"][0]

    except (httpx.HTTPError, ValueError, KeyError, IndexError, TypeError) as exc:
        raise EmbeddingError(
            "Failed to generate embedding with Ollama"
        ) from exc

    if (
        len(embedding) != EMBEDDING_DIMENSIONS
        or not all(
            isinstance(value, (int, float)) and math.isfinite(value)
            for value in embedding
        )
    ):
        raise EmbeddingError(
            "Ollama returned an invalid embedding"
        )

    return [float(value) for value in embedding]
