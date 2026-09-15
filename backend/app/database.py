"""Async SQLAlchemy engine + session factory (SQLite by default, swap to Postgres)."""
from __future__ import annotations

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


def _to_async_url(url: str) -> str:
    """Convert sync DB URLs (e.g. sqlite:///) to async (sqlite+aiosqlite:///)."""
    if url.startswith("sqlite:///") and "aiosqlite" not in url:
        return url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
    return url


DATABASE_URL = _to_async_url(settings.DATABASE_URL)
engine = create_async_engine(DATABASE_URL, echo=False, future=True)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session
