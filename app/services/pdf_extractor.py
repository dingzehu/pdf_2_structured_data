import io

import pdfplumber


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract all text from a PDF given its raw bytes, concatenated page by page."""
    pages: list[str] = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:  # BytesIO wraps bytes so pdfplumber treats them as a file
        for page in pdf.pages:
            text = page.extract_text() or ""  # pdfplumber returns None for image-only pages - or "" prevents join() crash
            pages.append(text)
    return "\n\n".join(pages)
