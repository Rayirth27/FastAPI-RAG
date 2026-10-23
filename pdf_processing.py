from io import BytesIO

from pypdf import PdfReader
from pypdf.errors import PdfReadError


MAX_PAGES = 20
MAX_EXTRACTED_CHARS = 100_000


class PDFProcessingError(ValueError):
    pass


def extract_pdf_text(content: bytes) -> str:
    try:
        reader = PdfReader(BytesIO(content), strict=True)

        if reader.is_encrypted:
            raise PDFProcessingError(
                "Encrypted PDFs are not supported"
            )

        if len(reader.pages) == 0:
            raise PDFProcessingError("PDF has no pages")

        if len(reader.pages) > MAX_PAGES:
            raise PDFProcessingError(
                f"PDF exceeds {MAX_PAGES} pages"
            )

        extracted_pages = []
        total_chars = 0

        for page in reader.pages:
            text = page.extract_text() or ""

            total_chars += len(text)

            if total_chars > MAX_EXTRACTED_CHARS:
                raise PDFProcessingError(
                    "PDF contains too much extracted text"
                )

            extracted_pages.append(text)

        extracted_text = "\n".join(extracted_pages).strip()

        if not extracted_text:
            raise PDFProcessingError(
                "PDF contains no extractable text"
            )

        return extracted_text

    except PdfReadError as exc:
        raise PDFProcessingError(
            "Malformed PDF document"
        ) from exc
