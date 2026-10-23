import pytest
from pypdf import PdfWriter

from pdf_processing import PDFProcessingError

from io import BytesIO

from reportlab.pdfgen import canvas

from pdf_processing import extract_pdf_text

def test_extract_pdf_text():
    # Create a PDF in memory
    buffer = BytesIO()

    pdf = canvas.Canvas(buffer)
    pdf.drawString(
        72, 750,
        "FastAPI RAG successfully extracts PDF text."
    )
    pdf.save()

    # Extract text using our actual function
    content = buffer.getvalue()
    extracted_text = extract_pdf_text(content)

    # Verify the expected text was extracted
    assert "FastAPI RAG successfully extracts PDF text." in extracted_text



def make_pdf(page_count=1, password=None):
    writer = PdfWriter()

    for _ in range(page_count):
        writer.add_blank_page(width=595, height=842)

    if password:
        writer.encrypt(user_password=password)

    buffer = BytesIO()
    writer.write(buffer)

    return buffer.getvalue()


def test_rejects_malformed_pdf():
    fake_pdf = b"%PDF-1.4\nThis is not a valid PDF"

    with pytest.raises(PDFProcessingError):
        extract_pdf_text(fake_pdf)


def test_rejects_encrypted_pdf():
    content = make_pdf(password="test-password")

    with pytest.raises(
        PDFProcessingError,
        match="Encrypted PDFs are not supported",
    ):
        extract_pdf_text(content)


def test_rejects_pdf_with_too_many_pages():
    content = make_pdf(page_count=21)

    with pytest.raises(
        PDFProcessingError,
        match="PDF exceeds 20 pages",
    ):
        extract_pdf_text(content)


def test_rejects_pdf_without_text():
    content = make_pdf(page_count=1)

    with pytest.raises(
        PDFProcessingError,
        match="PDF contains no extractable text",
    ):
        extract_pdf_text(content)

