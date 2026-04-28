import asyncio
import uuid
import traceback

from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas import research
from app.db.models import ResearchJob, JobStatus
from app.db.postgres import get_db
from app.services.job_services import run_pipeline_safe
from app.db.postgres import AsyncSessionLocal

research_router = APIRouter()


# -------------------------
# START
# -------------------------
@research_router.post("/start")
async def start_research(
    request: Request,
    body: research.StartResearchRequest,
    db: AsyncSession = Depends(get_db)
):
    print("\n📩 /start called")

    new_job = ResearchJob(
        id=uuid.uuid4(),
        question=body.question,
        status=JobStatus.running
    )

    db.add(new_job)
    await db.commit()
    await db.refresh(new_job)

    print(f"🆕 Job created: {new_job.id}")

    graph = request.app.state.graph

    # ❗ DO NOT pass db session
    asyncio.create_task(
        run_pipeline_safe(body.question, str(new_job.id), graph)
    )

    return {"id": str(new_job.id)}


# -------------------------
# STATUS
# -------------------------
@research_router.get("/{job_id}/status")
async def get_research_status(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    print(f"🔄 Polling status for job_id={job_id}")

    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(400, "Invalid job ID")

    result = await db.execute(
        select(ResearchJob).where(ResearchJob.id == job_uuid)
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(404, "Job not found")

    # ✅ Convert subtasks → AgentStep format
    steps = [
        {
            "id": str(i),
            "name": step,
            "status": "complete" if job.status == JobStatus.complete else "running",
        }
        for i, step in enumerate(job.subtasks or [])
    ]

    return {
        "id": str(job.id),
        "question": job.question,
        "status": job.status.value if hasattr(job.status, "value") else job.status,
        "steps": steps,
        "report": job.report,
        "flaggedClaims": [],
    }


# -------------------------
# GET FULL JOB (NEW)
# -------------------------
@research_router.get("/{job_id}")
async def get_research(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(400, "Invalid job ID")

    result = await db.execute(
        select(ResearchJob).where(ResearchJob.id == job_uuid)
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(404, "Job not found")

    return {
        "id": str(job.id),
        "question": job.question,
        "status": job.status.value if hasattr(job.status, "value") else job.status,
        "steps": job.subtasks or [],
        "report": job.report,
    }


# -------------------------
# APPROVE (HITL)
# -------------------------
from langgraph.types import Command

from langgraph.types import Command
from sqlalchemy import select
from app.db.postgres import AsyncSessionLocal

@research_router.post("/{job_id}/approve")
async def approve_research(job_id: str, body: dict, request: Request):
    graph = request.app.state.graph
    approved = body.get("action") == "approve"

    try:
        final_state = await graph.ainvoke(
            Command(resume=approved),
            config={"configurable": {"thread_id": job_id}},
        )

        print("🧠 RESUMED FINAL STATE:", final_state)

        # ✅ SAVE TO DB (THIS WAS MISSING)
        async with AsyncSessionLocal() as session:
            job_uuid = uuid.UUID(job_id)

            result = await session.execute(
                select(ResearchJob).where(ResearchJob.id == job_uuid)
            )
            job = result.scalar_one_or_none()

            if job:
                job.status = JobStatus.complete
                job.report = final_state.get("report")
                job.subtasks = final_state.get("subtasks", [])
                job.findings = final_state.get("findings", {})
                await session.commit()

    except Exception:
        traceback.print_exc()
        raise HTTPException(500, "Failed to resume graph")

    return {"success": True}