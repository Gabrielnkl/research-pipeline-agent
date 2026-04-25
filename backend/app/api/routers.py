# FastAPI REST API
#     │
#     ├── POST /research/start        → Starts a new research job
#     ├── GET  /research/{id}/status  → Polls job state
#     ├── POST /research/{id}/approve → Human approves/rejects a checkpoint
#     └── GET  /research/{id}/report  → Returns final report
# [ ] Create POST /research/start endpoint — accepts { question: string }, creates job, returns { job_id }
# [ ] Create GET /research/{id}/status endpoint — returns full job state
# [ ] Write a smoke test: start a job and poll its status


from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from schemas import research
from db.dependencies import get_db
from db.models import ResearchJob
import uuid

from sqlalchemy import select


research_router = APIRouter()


@research_router.post("/start")
async def start_research(
    request: research.StartResearchRequest,
    db: AsyncSession = Depends(get_db)
):
    new_job = ResearchJob(
        id=uuid.uuid4(),
        question=request.question
    )

    db.add(new_job)
    await db.commit()
    await db.refresh(new_job)

    return {"job_id": str(new_job)}



@research_router.get("/{job_id}/status")
async def get_research_status(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job ID format")

    result = await db.execute(
        select(ResearchJob).where(ResearchJob.id == job_uuid)
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "job_id": str(job.id),
        "question": job.question,
        "status": job.status.value,
        "subtasks": job.subtasks,
        "findings": job.findings,
        "report": job.report,
        "created_at": job.created_at.isoformat(),
        "updated_at": job.updated_at.isoformat() if job.updated_at else None
    }


# [ ] Create POST /research/{id}/approve endpoint:
# Accepts { approved: bool, feedback: string }
# If approved: resumes graph with feedback → continues to report_writer
# If rejected: resumes graph → loops back to web_search with feedback as additional context

@research_router.post("/{job_id}/approve")
async def approve_checkpoint(
    job_id: str,
    request: research.ApproveCheckpointRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job ID format")

    result = await db.execute(
        select(ResearchJob).where(ResearchJob.id == job_uuid)
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Here you would add logic to update the job based on approval/rejection
    # For example, you might set a flag in the database that the graph can check

    return {"message": "Checkpoint updated successfully"}