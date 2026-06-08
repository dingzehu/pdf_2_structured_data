import io

import pdfplumber


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract all text from a PDF given its raw bytes, concatenated page by page."""
    pages: list[str] = []
    # BytesIO wraps bytes so pdfplumber treats them as a file
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            # pdfplumber returns None for image-only pages; or "" prevents join() crash
            text = page.extract_text() or ""
            pages.append(text)
    return "\n\n".join(pages)
