# pdf-to-structured-data

A production-ready ETL pipeline that extracts structured data from PDF documents
using Google Gemini AI, validates the output with Pydantic v2, stores results in
PostgreSQL, and exposes the whole pipeline as a REST API — all runnable with a
single `docker compose up` command.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                        CLIENT                           │
│               POST /extract  (PDF file)                 │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│                  FASTAPI  (port 8000)                   │
│                                                         │
│  routes.py ──► pipeline.py                              │
│                    │                                    │
│           ┌────────┴────────┐                           │
│           ▼                 ▼                           │
│  pdf_extractor.py    gemini_client.py                   │
│  (pdfplumber)        (google-genai)                     │
│           │                 │                           │
│           │   raw text      │   structured JSON         │
│           └────────┬────────┘                           │
│                    ▼                                    │
│            Pydantic v2  (validate + type-check)         │
│                    │                                    │
│            SQLAlchemy 2.0  (async write)                │
└────────────────────┼────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              POSTGRESQL 16  (port 5432)                 │
│              table: extraction_records                  │
└─────────────────────────────────────────────────────────┘
```

---

## Features

- **PDF ingestion** — accepts any text-based PDF via multipart upload
- **LLM extraction** — Google Gemini 2.0 Flash extracts 10 structured fields
- **Strict validation** — Pydantic v2 rejects malformed or incomplete LLM output
- **Async persistence** — SQLAlchemy 2.0 async ORM writes results to PostgreSQL
- **REST API** — four endpoints: extract, retrieve by ID, paginated list, health check
- **One-command deploy** — Docker Compose orchestrates API + database with health checks
- **Full test suite** — pytest with async fixtures, mocked Gemini, real DB integration tests
- **CI/CD** — GitHub Actions runs linting and tests on every push

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| API framework | FastAPI + Uvicorn |
| LLM | Google Gemini 2.0 Flash (`google-genai`) |
| PDF parsing | pdfplumber |
| Validation | Pydantic v2 |
| ORM | SQLAlchemy 2.0 (async) |
| Database | PostgreSQL 16 |
| Containers | Docker + Docker Compose |
| Testing | pytest + pytest-asyncio + httpx |
| Linting | ruff |

---

## Project Structure

```
pdf-to-structured-data/
├── app/
│   ├── main.py              # FastAPI app factory + lifespan
│   ├── config.py            # Settings via pydantic-settings
│   ├── database.py          # Async engine + session factory
│   ├── models/
│   │   ├── db.py            # SQLAlchemy ORM models
│   │   └── schemas.py       # Pydantic v2 request/response models
│   ├── services/
│   │   ├── pdf_extractor.py # pdfplumber text extraction
│   │   ├── gemini_client.py # Google Gemini API client
│   │   └── pipeline.py      # Orchestration: PDF → LLM → DB
│   └── api/
│       └── routes.py        # FastAPI route handlers
├── tests/                   # pytest suite (unit + integration)
├── sample_pdfs/             # synthetic test PDFs
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── .env.example
```

---

## Quickstart

### Prerequisites

- Docker + Docker Compose
- A [Google Gemini API key](https://aistudio.google.com/app/apikey)

### 1. Clone and configure

```bash
git clone https://github.com/your-username/pdf-to-structured-data.git
cd pdf-to-structured-data
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### 2. Start the stack

```bash
docker compose up --build
```

The API is now available at `http://localhost:8000`.

### 3. Extract data from a PDF

```bash
curl -X POST http://localhost:8000/extract \
  -F "file=@sample_pdfs/sample_invoice.pdf"
```

---

## API Reference

### `POST /extract`

Upload a PDF and receive structured extracted data.

**Request:** `multipart/form-data` with a `file` field (PDF only)

**Response `201`:**
```json
{
  "record_id": 1,
  "filename": "invoice.pdf",
  "extraction": {
    "document_type": "invoice",
    "issuer_name": "Acme Corp",
    "recipient_name": "John Doe",
    "document_date": "2024-01-15",
    "document_number": "INV-001",
    "total_amount": 1500.00,
    "currency": "USD",
    "line_items": [
      {
        "description": "Consulting",
        "quantity": 10,
        "unit_price": 150.0,
        "total": 1500.0
      }
    ],
    "summary": "Invoice from Acme Corp to John Doe for consulting services.",
    "raw_confidence": 0.97
  },
  "created_at": "2024-01-15T12:00:00Z"
}
```

**Errors:** `422` if validation fails, `500` if Gemini is unavailable.

---

### `GET /results/{record_id}`

Retrieve a stored extraction by database ID.

**Response `200`:** same schema as `POST /extract`  
**Response `404`:** record not found

---

### `GET /results?page=1&size=10`

Paginated list of all past extractions, newest first.

**Response `200`:**
```json
{
  "total": 42,
  "page": 1,
  "size": 10,
  "results": [...]
}
```

---

### `GET /health`

Service health check.

**Response `200`:**
```json
{ "status": "ok", "db": "connected", "gemini": "reachable" }
```

---

## Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests with coverage
pytest --cov=app tests/

# Run linter
ruff check .
```

> **Note:** Integration tests require a running PostgreSQL instance.
> Set `DATABASE_URL` in `.env` to point at your test database.

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `GEMINI_API_KEY` | *(required)* | Your Google Gemini API key |
| `DATABASE_URL` | `postgresql+asyncpg://postgres:password@db:5432/pdf_extractions` | PostgreSQL connection string |
| `GEMINI_MODEL` | `gemini-2.0-flash` | Gemini model name |

See `.env.example` for the full template.

---

## License

MIT
