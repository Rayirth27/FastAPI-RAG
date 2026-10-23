
import pytest

from chunking import chunk_text


def test_chunk_text_with_overlap():
    chunks = chunk_text(
        "ABCDEFGHIJ",
        chunk_size=6,
        overlap=2,
    )

    assert chunks == ["ABCDEF", "EFGHIJ"]


def test_chunk_text_empty_input():
    assert chunk_text("   ") == []


def test_chunk_text_invalid_overlap():
    with pytest.raises(ValueError):
        chunk_text(
            "Hello World",
            chunk_size=5,
            overlap=5,
        )
