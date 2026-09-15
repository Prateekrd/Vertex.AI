"""Application configuration — reads env vars, sensible defaults."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./app/harmonization.db"
    REDIS_URL: str = "redis://localhost:6379/0"

    # ML
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    FAISS_METRIC: str = "ip"  # inner product == cosine on normalized vectors

    # Matching thresholds
    CLUSTER_THRESHOLD: float = 0.70
    HIGH_CONFIDENCE: float = 0.85
    MEDIUM_CONFIDENCE: float = 0.65

    # LLM augmentation (optional — disable for offline use)
    LLM_API_KEY: Optional[str] = None
    LLM_PROVIDER: str = "auto"  # auto | anthropic | openai | none
    LLM_MODEL: str = "claude-3-haiku-20240307"
    LLM_ENABLED: bool = False

    # Paths — resolve relative to project root (backend/../../)
    DATA_DIR: Path = Path(__file__).resolve().parent.parent.parent / "data"
    UPLOAD_DIR: Path = Path(__file__).resolve().parent.parent.parent / "uploads"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
