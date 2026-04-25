# db/dependencies.py

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.postgres import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides a database session.

    - Creates a new async session per request
    - Yields it to the endpoint
    - Ensures it is properly closed after use
    """
    async with AsyncSessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()