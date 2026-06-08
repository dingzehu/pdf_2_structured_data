from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.database import engine
from app.models.db import Base


@asynccontextmanager  # turns an async generator into a context manager FastAPI can use
async def lifespan(app: FastAPI):
    """Create database tables on startup."""
    async with engine.begin() as conn:
        # create_all is sync - run_sync bridges it into async
        await conn.run_sync(Base.metadata.create_all)
    yield  # startup done - lifespan pauses here while the server handles requests


app = FastAPI(
    title="pdf-to-structured-data",
    description="Extract structured data from PDF files using Gemini AI.",
    version="0.1.0",
    lifespan=lifespan,  # replaces deprecated @app.on_event("startup") pattern
)

app.include_router(router)
