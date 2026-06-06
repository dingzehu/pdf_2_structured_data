from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.db import ExtractionRecord
from app.models.schemas import (
    ExtractedDocument,
    ExtractionResponse,
    HealthResponse,
    LineItem,
    PaginatedResultsResponse,
)
from app.services.pipeline import run_pipeline

router = APIRouter()


@router.post("/extract", response_model=ExtractionResponse, status_code=201)  # 201 Created, not 200 OK
async def extract_pdf(
    file: UploadFile = File(...),  # File(...) means the upload field is required
    db: AsyncSession = Depends(get_db),  # FastAPI calls get_db() and injects the session automatically
) -> ExtractionResponse:
    """Accept a PDF upload and run the full extraction pipeline."""
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=422, detail="Uploaded file must be a PDF.")
    file_bytes = await file.read()
    try:
        return await run_pipeline(file_bytes, file.filename or "unknown.pdf", db)  # or "unknown.pdf" handles None filename
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors()) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Extraction failed.") from exc


@router.get("/results/{record_id}", response_model=ExtractionResponse)
async def get_result(
    record_id: int,
    db: AsyncSession = Depends(get_db),
) -> ExtractionResponse:
    """Return a single extraction result by its database ID."""
    record = await db.get(ExtractionRecord, record_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Record {record_id} not found.")
    return _record_to_response(record)


@router.get("/results", response_model=PaginatedResultsResponse)
async def list_results(
    page: int = Query(1, ge=1),  # ge=1 means minimum value is 1- validated automatically
    size: int = Query(10, ge=1, le=100),  # le=100 caps page size to prevent huge DB queries
    db: AsyncSession = Depends(get_db),
) -> PaginatedResultsResponse:
    """Return a paginated list of all past extractions, newest first."""
    offset = (page - 1) * size

    count_result = await db.execute(select(func.count()).select_from(ExtractionRecord))
    total = count_result.scalar_one()

    rows_result = await db.execute(
        select(ExtractionRecord)
        .order_by(ExtractionRecord.id.desc())
        .offset(offset)
        .limit(size)
    )
    records = rows_result.scalars().all()

    return PaginatedResultsResponse(
        total=total,
        page=page,
        size=size,
        results=[_record_to_response(r) for r in records],
    )


@router.get("/health", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    """Check database connectivity and return service status."""
    try:
        await db.execute(select(1))  # cheapest possible query - just check DB is reachable
        db_status = "connected"
    except Exception:
        db_status = "error"
    return HealthResponse(status="ok", db=db_status, gemini="reachable")  # gemini hardcoded - no live API check


def _record_to_response(record: ExtractionRecord) -> ExtractionResponse:
    """Convert an ORM record back into the API response schema."""
    extraction = ExtractedDocument(
        document_type=record.document_type,
        issuer_name=record.issuer_name,
        recipient_name=record.recipient_name,
        document_date=record.document_date,
        document_number=record.document_number,
        total_amount=record.total_amount,
        currency=record.currency,
        line_items=[LineItem(**item) for item in (record.line_items or [])],  # or [] guards against NULL in DB
        summary=record.summary,
        raw_confidence=record.raw_confidence,
    )
    return ExtractionResponse(
        record_id=record.id,
        filename=record.filename,
        extraction=extraction,
        created_at=record.created_at,
    )
