"""FastAPI dependency providers."""
from __future__ import annotations

from typing import AsyncGenerator, Optional
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.database import async_session, AsyncSession

security = HTTPBearer(auto_error=False)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that provides a database session."""
    async with async_session() as session:
        yield session


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> Optional[str]:
    """For hackathon: no real auth. Replace with real auth if needed."""
    return "demo_user"
