Complete dependency list — what we need and why                                
                                                                                 
  ┌─────────────────────┬─────────────────────────────────────────────────────┐  
  │       Package       │                         Why                         │
  ├─────────────────────┼─────────────────────────────────────────────────────┤  
  │                     │ The REST API framework. Async-native,               │
  │ fastapi             │ auto-generates OpenAPI docs, handles request        │  
  │                     │ validation via Pydantic automatically.              │
  ├─────────────────────┼─────────────────────────────────────────────────────┤  
  │ uvicorn[standard]   │ The ASGI server that runs FastAPI. [standard] adds  │  
  │                     │ uvloop (faster event loop) and websockets.          │  
  ├─────────────────────┼─────────────────────────────────────────────────────┤  
  │                     │ Extracts text from PDFs with good table and layout  │
  │ pdfplumber          │ awareness — better than PyPDF2 for structured       │  
  │                     │ documents.                                          │  
  ├─────────────────────┼─────────────────────────────────────────────────────┤
  │ google-genai        │ The newer Google Gen AI SDK. Provides genai.Client  │  
  │                     │ with client.models.generate_content(...).           │
  ├─────────────────────┼─────────────────────────────────────────────────────┤  
  │                     │ Data validation. v2 is 5–50× faster than v1 (Rust   │
  │ pydantic            │ core). Used for both API schemas and Gemini output  │  
  │                     │ validation.                                         │
  ├─────────────────────┼─────────────────────────────────────────────────────┤  
  │                     │ BaseSettings subclass that reads from .env files    │
  │ pydantic-settings   │ and environment variables — the standard way to     │  
  │                     │ handle config in FastAPI apps.                      │
  ├─────────────────────┼─────────────────────────────────────────────────────┤  
  │                     │ ORM for PostgreSQL. [asyncio] extra installs        │  
  │ sqlalchemy[asyncio] │ greenlet, which SQLAlchemy needs internally to      │
  │                     │ bridge sync/async boundaries.                       │  
  ├─────────────────────┼─────────────────────────────────────────────────────┤
  │                     │ The async PostgreSQL driver. SQLAlchemy's async     │  
  │ asyncpg             │ dialect (postgresql+asyncpg://) uses it under the   │
  │                     │ hood.                                               │  
  ├─────────────────────┼─────────────────────────────────────────────────────┤
  │                     │ Required by FastAPI to parse multipart/form-data    │  
  │ python-multipart    │ (file uploads). Without it, POST /extract will      │
  │                     │ error at startup.                                   │  
  ├─────────────────────┼─────────────────────────────────────────────────────┤
  │ python-dotenv       │ Loads .env files into os.environ —                  │  
  │                     │ pydantic-settings uses this automatically.          │
  ├─────────────────────┼─────────────────────────────────────────────────────┤  
  │ Dev only            │                                                     │
  ├─────────────────────┼─────────────────────────────────────────────────────┤  
  │ pytest              │ Test runner.                                        │
  ├─────────────────────┼─────────────────────────────────────────────────────┤  
  │ pytest-asyncio      │ Teaches pytest how to run async def test_*          │
  │                     │ functions.                                          │  
  ├─────────────────────┼─────────────────────────────────────────────────────┤
  │ httpx               │ The async HTTP client — used as the test transport  │  
  │                     │ layer for FastAPI's AsyncClient.                    │
  ├─────────────────────┼─────────────────────────────────────────────────────┤
  │ pytest-cov          │ Coverage reporting (--cov=app).                     │  
  ├─────────────────────┼─────────────────────────────────────────────────────┤
  │                     │ Extremely fast linter + formatter (written in       │  
  │ ruff                │ Rust). Replaces flake8, isort, pyupgrade in one     │
  │                     │ tool.                                               │  
  └─────────────────────┴─────────────────────────────────────────────────────┘  
                                     