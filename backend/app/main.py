"""Main FastAPI application."""
from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import Base, engine
from app.api.routes import upload, processing, review, metrics, search
from app.api.routes.standard_codes import router as standard_codes_router
from app.api.websocket import ws_manager

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create DB tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    # Cleanup
    await engine.dispose()


app = FastAPI(
    title="SIH 26099 — Material Code Harmonization API",
    description="AI-Driven Standardization and Harmonization of Material Codes Across CPSEs",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend
frontend_path = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=os.path.join(frontend_path, "assets")), name="static")


# Routes
app.include_router(upload.router, prefix="/api/v1/upload", tags=["upload"])
app.include_router(processing.router, prefix="/api/v1/process", tags=["process"])
app.include_router(review.router, prefix="/api/v1/review", tags=["review"])
app.include_router(metrics.router, prefix="/api/v1/metrics", tags=["metrics"])
app.include_router(search.router, prefix="/api/v1/search", tags=["search"])
app.include_router(standard_codes_router, prefix="/api/v1/codes", tags=["codes"])



@app.get("/")
def read_root():
    return {"message": "SIH 26099 Material Harmonization API", "version": "0.1.0"}


@app.get("/health")
def health():
    return {"status": "healthy", "llm_enabled": settings.LLM_ENABLED}


@app.get("/debug/data-dir")
def debug_data_dir():
    """Debug endpoint: show what DATA_DIR resolves to and what files are there."""
    import os
    d = settings.DATA_DIR
    return {
        "data_dir_str": str(d),
        "data_dir_exists": d.exists(),
        "cwd": os.getcwd(),
        "files": [f.name for f in d.glob("cpse_*_materials.csv")] if d.exists() else [],
    }
