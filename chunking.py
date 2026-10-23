def chunk_text(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 150,
) -> list[str]:

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "overlap must be non-negative and smaller than chunk_size"
        )

    normalized = " ".join(text.split())

    if not normalized:
        return []

    chunks = []
    step = chunk_size - overlap

    for start in range(0, len(normalized), step):
        end = start + chunk_size
        chunks.append(normalized[start:end])

        if end >= len(normalized):
            break

    return chunks
