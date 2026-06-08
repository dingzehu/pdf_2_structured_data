import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import ValidationError

from app.services.gemini_client import GeminiClient

VALID_PAYLOAD = {
    "document_type": "invoice",
    "issuer_name": "Acme Corp",
    "recipient_name": "John Doe",
    "document_date": "2024-01-15",
    "document_number": "INV-001",
    "total_amount": 100.0,
    "currency": "USD",
    "line_items": [],
    "summary": "An invoice from Acme Corp to John Doe.",
    "raw_confidence": 0.95,
    }


async def test_extract_document_returns_extracted_document():
    """Happy path: valid Gemini response is parsed into ExtractedDocument."""
    mock_response = MagicMock()  # fake Gemini response object
    mock_response.text = json.dumps(VALID_PAYLOAD)  # .text is what our code reads

    # replace genai.Client inside gemini_client.py for this block only
    with patch("app.services.gemini_client.genai.Client") as mock_client_cls:
        # AsyncMock make generate_content awaitable
        mock_client_cls.return_value.aio.models.generate_content = AsyncMock(
            return_value=mock_response
        )
        client = GeminiClient()  # __init__ now gets the fake client
        result = await client.extract_document("Some invoice text")

    assert result.document_type == "invoice"
    assert result.issuer_name == "Acme Corp"
    assert result.raw_confidence == 0.95


async def test_extract_document_raises_on_invalid_json():
    """If Gemini returns non-JSON text, json.JSONDecodeError is raised."""
    mock_response = MagicMock()  # fake response object
    # Gemini occasionally returns plain text instead of JSON
    mock_response.text = "Sorry, I cannot process this document."

    with patch("app.services.gemini_client.genai.Client") as mock_client_cls:
        mock_client_cls.return_value.aio.models.generate_content = AsyncMock(
            return_value=mock_response
        )
        client = GeminiClient()
        with pytest.raises(json.JSONDecodeError):  # our code does not catch this
            await client.extract_document("Some text")


async def test_extract_document_raises_on_invalid_schema():
    """If Gemini returns JSON that does not match the schema,
    ValidationError is raised."""
    mock_response = MagicMock()  # fake response object
    # valid JSON, but fields don't match ExtractedDocument schema
    mock_response.text = json.dumps({"wrong_field": "wrong_value"})

    with patch("app.services.gemini_client.genai.Client") as mock_client_cls:
        mock_client_cls.return_value.aio.models.generate_content = AsyncMock(
            return_value=mock_response
        )
        client = GeminiClient()
        with pytest.raises(ValidationError):  # Pydantic rejects the wrong shape
            await client.extract_document("Some text")
