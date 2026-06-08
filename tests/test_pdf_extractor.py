from unittest.mock import MagicMock, patch

from app.services.pdf_extractor import extract_text_from_pdf


def test_single_page_pdf_returns_text():
    """Text from a single-page PDF is returned as-is."""
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Invoice total: €100"

    with patch("app.services.pdf_extractor.pdfplumber.open") as mock_open:
        mock_open.return_value.__enter__.return_value.pages = [mock_page]
        result = extract_text_from_pdf(b"fake-pdf-bytes")

    assert result == "Invoice total: €100"


def test_multi_page_pdf_joins_with_double_newline():
    """Pages are joined with a double newline."""
    page1 = MagicMock()
    page1.extract_text.return_value = "Page one"
    page2 = MagicMock()
    page2.extract_text.return_value = "Page two"

    with patch("app.services.pdf_extractor.pdfplumber.open") as mock_open:
        mock_open.return_value.__enter__.return_value.pages = [page1, page2]
        result = extract_text_from_pdf(b"fake-pdf-bytes")

    assert result == "Page one\n\nPage two"


def test_page_with_no_text_returns_empty_string():
    """Pages where pdfplumber returns None are converted to empty string."""
    mock_page = MagicMock()
    mock_page.extract_text.return_value = None

    with patch("app.services.pdf_extractor.pdfplumber.open") as mock_open:
        mock_open.return_value.__enter__.return_value.pages = [mock_page]
        result = extract_text_from_pdf(b"fake-pdf-bytes")

    assert result == ""
