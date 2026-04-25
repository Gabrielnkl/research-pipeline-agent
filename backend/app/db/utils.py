from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import ResearchJob


async def update_job(db: AsyncSession, job_id: str, **fields):
    await db.execute(
        update(ResearchJob)
        .where(ResearchJob.id == job_id)
        .values(**fields)
    )
    await db.commit()