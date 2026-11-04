import pytest
from pydantic import ValidationError

from main import Document


# Test 1: Valid input and normalization
def test_valid_document_normalization():
    document = Document(
        title="  Employee Policy  ",
        content="\n All employees use SSO. \t",
    )

    assert document.title == "Employee Policy"
    assert document.content == "All employees use SSO."


# Test 2: Maximum allowed length
def test_document_accepts_boundary_lengths():
    document = Document(
        title="T" * 200,
        content="C" * 20000,
    )

    assert len(document.title) == 200
    assert len(document.content) == 20000


# Tests 3–11: Invalid inputs
@pytest.mark.parametrize(
    "payload",
    [
        {"title": "   ", "content": "Valid content"},
        {"title": "Policy", "content": " \n "},
        {"title": "T" * 201, "content": "Valid content"},
        {"title": "Policy", "content": "C" * 20001},
        {"content": "Valid content"},
        {"title": "Policy"},
        {"title": None, "content": "Valid content"},
        {"title": "Policy", "content": None},
        {"title": 123, "content": "Valid content"},
    ],
)
def test_invalid_document_is_rejected(payload):
    with pytest.raises(ValidationError):
        Document.model_validate(payload)
