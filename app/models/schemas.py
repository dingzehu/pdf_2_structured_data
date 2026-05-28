from datetime import date, datetime

from pydantic import BaseModel, field_validator


class LineItem(BaseModel):
    """A single line in a document (invoice row, contract clause, etc.)."""

    description: str
    quantity: float | None = None
    unit_price: float | None = None
    total: float | None = None


class ExtractedDocument(BaseModel):
    """Structured data extracted from a PDF by the Gemini LLM.

    raw_confidence is a self-assessed value: the prompt explicitly asks
    Gemini to rate how complete and clear the document data was (0.0–1.0).
    It is NOT a token-level probability from the model API.
    """

    document_type: str
    issuer_name: str | None = None
    recipient_name: str | None = None
    document_date: date | None = None
    document_number: str | None = None
    total_amount: float | None = None
    currency: str | None = None
    line_items: list[LineItem] = []
    summary: str
    raw_confidence: float

    @field_validator("currency")
    @classmethod
    def uppercase_currency(cls, v: str | None) -> str | None:
        return v.upper() if v else v


class ExtractionResponse(BaseModel):
    """Returned by POST /extract and GET /results/{record_id}."""

    record_id: int
    filename: str
    extraction: ExtractedDocument
    created_at: datetime


class PaginatedResultsResponse(BaseModel):
    """Returned by GET /results with pagination metadata."""

    total: int
    page: int
    size: int
    results: list[ExtractionResponse]


class HealthResponse(BaseModel):
    """Returned by GET /health."""

    status: str
    db: str
    gemini: str
