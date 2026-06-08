from datetime import date, datetime
from unittest.mock import AsyncMock, patch

from app.models.db import ExtractionRecord
from app.models.schemas import ExtractedDocument, ExtractionResponse

MOCK_EXTRACTION = ExtractedDocument(
    document_type="invoice",
    issuer_name="Acme Corp",
    recipient_name="John Doe",
    document_date=date(2024, 1, 15),  # real data object,  not a string
    document_number="INV-001",
    total_amount=100.0,
    currency="USD",
    line_items=[],  # empty list - no line items needed for route tests
    summary="An invoice from Acme Corp.",
    raw_confidence=0.9,
)


async def test_post_extract_returns_structured_data(client):
    """POST /extract: pipeline mocked; verifies route serialises the response
    correctly."""
    # build the fake return value that run_pipeline would normally produce
    mock_result = ExtractionResponse(
        record_id=1,
        filename="test.pdf",
        extraction=MOCK_EXTRACTION,
        created_at=datetime(2024, 1, 15, 12, 0, 0)  # required by ExtractionResponse
    )

    # replace run_pipeline in routes.py with an async fake for this block only
    with patch("app.api.routes.run_pipeline", new_callable=AsyncMock) as mock_pipeline:
        mock_pipeline.return_value = mock_result  # fake returns our mock result
        response = await client.post(
            "/extract",
            # multipart/form-data: (filename, bytes, content-type)
            files={"file": ("test.pdf", b"fake-pdf-bytes", "application/pdf")}
        )

    assert response.status_code == 201  # routes.py declares status_code=201
    data = response.json()
    assert data["filename"] == "test.pdf"
    assert data["extraction"]["document_type"] == "invoice"


async def test_post_extract_returns_500_on_pipeline_error(client):
    """POST /extract: if run_pipeline raises an unexpected error, 500 is returned."""
    # replace run_pipeline with a fake that raises instead of returning
    with patch("app.api.routes.run_pipeline", new_callable=AsyncMock) as mock_pipeline:
        # side_effect means "when called, raised this exception instead of returning"
        mock_pipeline.side_effect = Exception("Gemini unavailable")
        response = await client.post(
            "/extract",
            files={"file": ("test.pdf", b"fake-pdf-bytes", "application/pdf")},
        )

    assert response.status_code == 500


async def test_get_result_returns_stored_record(client, db_session):
    """GET /results/{id}: inserts a record directly into DB, retrieves it via API."""
    # create a real ORM record and save it to the test database
    record = ExtractionRecord(
        filename="invoice.pdf",
        document_type="invoice",
        issuer_name="Acme Corp",
        recipient_name=None,
        document_date=None,
        document_number=None,
        total_amount=100.0,
        currency="USD",
        line_items=[],  # JSON column -- empty list is valid
        summary="Test invoice.",
        raw_confidence=0.9,
    )
    db_session.add(record)            # stage the record
    await db_session.commit()         # write to the test DB
    await db_session.refresh(record)  # populate record.id and record.created_at

    response = await client.get(f"/results/{record.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "invoice.pdf"
    assert data["extraction"]["issuer_name"] == "Acme Corp"


async def test_get_result_returns_404_for_missing_record(client):
    """GET /results/{id}: returns 404 when no record exists with that ID."""
    # 99999 is an ID that will never exist in the empty test database
    response = await client.get("/results/99999")

    assert response.status_code == 404


async def test_get_results_returns_paginated_list(client, db_session):
    """GET /results: inserts two records, verifies both appear in the
    paginated response."""
    # insert two records directly into the test DB
    for i in range(2):
        record = ExtractionRecord(
            filename=f"invoice_{i}.pdf",  # unique filename per record
            document_type="invoice",
            issuer_name=f"Company {i}",  # unique issuer per record
            recipient_name=None,
            document_date=None,
            document_number=None,
            total_amount=None,
            currency=None,
            line_items=[],
            summary=f"Invoice number {i}",  # unique summary per record
            raw_confidence=0.8,
        )
        db_session.add(record)  # stage each record inside the loop
    await db_session.commit()  # write both records in one commit after the loop

    response = await client.get("/results?page=1&size=10")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2         # DB has exactly 2 records
    assert len(data["results"]) == 2  # response contains exactly 2 items


async def test_health_returns_ok(client):
    """GET /health: verifies the health endpoint reports all systems operational."""
    response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["db"] == "connected"   # confirms test DB is reachable

