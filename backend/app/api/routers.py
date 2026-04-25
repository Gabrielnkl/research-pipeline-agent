# import asyncio
# import uuid
# from fastapi import APIRouter, HTTPException, Depends
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select
# from app.db.dependencies import get_db
# from app.schemas import research
# from app.db.models import ResearchJob
# from app.graph.pipeline import ResearchPipeline, graph


# research_router = APIRouter()


# @research_router.post("/start")
# async def start_research(
#     request: research.StartResearchRequest,
#     db: AsyncSession = Depends(get_db)
# ):
#     new_job = ResearchJob(
#         id=uuid.uuid4(),
#         question=request.question,
#         status="running"
#     )

#     db.add(new_job)
#     await db.commit()
#     await db.refresh(new_job)

#     pipeline = ResearchPipeline()

#     # 🚀 background execution
#     asyncio.create_task(
#         pipeline.run_pipeline(request.question, str(new_job.id))
#     )

#     return {"id": str(new_job.id)}


# @research_router.get("/{job_id}/status")
# async def get_research_status(
#     job_id: str,
#     db: AsyncSession = Depends(get_db)
# ):
#     try:
#         job_uuid = uuid.UUID(job_id)
#     except ValueError:
#         raise HTTPException(400, "Invalid job ID")

#     result = await db.execute(
#         select(ResearchJob).where(ResearchJob.id == job_uuid)
#     )
#     job = result.scalar_one_or_none()

#     if not job:
#         raise HTTPException(404, "Job not found")

#     return {
#         "id": str(job.id),
#         "status": job.status,
#         "steps": job.subtasks or [],
#         "report": job.report,
#         "flaggedClaims": [],
#     }


# @research_router.post("/{job_id}/approve")
# async def approve_research(job_id: str, request: dict):
#     await graph.ainvoke(
#         {
#             "approved": request.get("approved", True),
#             "human_feedback": request.get("feedback", ""),
#             "retry_count": 1,
#         },
#         config={
#             "configurable": {
#                 "thread_id": job_id,
#                 "job_id": job_id
#             }
#         }
#     )

#     return {"status": "resumed"}
import asyncio
import uuid
import traceback

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.dependencies import get_db
from app.schemas import research
from app.db.models import ResearchJob
from app.graph.pipeline import ResearchPipeline, graph


research_router = APIRouter()


# -------------------------
# SAFE PIPELINE RUNNER
# -------------------------
async def run_pipeline_safe(pipeline, question, job_id):
    try:
        print(f"\n🚀 STARTING PIPELINE job_id={job_id}")
        print(f"❓ Question: {question}\n")

        await pipeline.run_pipeline(question, job_id)

        print(f"✅ PIPELINE FINISHED job_id={job_id}\n")

    except Exception as e:
        print(f"\n❌ PIPELINE ERROR job_id={job_id}")
        print("Error:", str(e))
        traceback.print_exc()
        print("\n")


# -------------------------
# START
# -------------------------
@research_router.post("/start")
async def start_research(
    request: research.StartResearchRequest,
    db: AsyncSession = Depends(get_db)
):
    print("\n📩 /start called")

    new_job = ResearchJob(
        id=uuid.uuid4(),
        question=request.question,
        status="running"
    )

    db.add(new_job)
    await db.commit()
    await db.refresh(new_job)

    print(f"🆕 Job created: {new_job.id}")

    pipeline = ResearchPipeline()

    # 🚀 background execution with debug
    asyncio.create_task(
        run_pipeline_safe(pipeline, request.question, str(new_job.id))
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

    print(f"📊 Status: {job.status} | Steps: {len(job.subtasks or [])}")

    return {
        "id": str(job.id),
        "status": job.status.value if hasattr(job.status, "value") else job.status,
        "steps": job.subtasks or [],
        "report": job.report,
        "flaggedClaims": [],
    }


# -------------------------
# APPROVE (HITL)
# -------------------------
@research_router.post("/{job_id}/approve")
async def approve_research(job_id: str, request: dict):
    print(f"\n🧑‍⚖️ HITL approval for job_id={job_id}")
    print(f"Approved: {request.get('approved')}")
    print(f"Feedback: {request.get('feedback')}\n")

    try:
        await graph.ainvoke(
            {
                "approved": request.get("approved", True),
                "human_feedback": request.get("feedback", ""),
                "retry_count": 1,
            },
            config={
                "configurable": {
                    "thread_id": job_id,
                    "job_id": job_id
                }
            }
        )
    except Exception as e:
        print("❌ ERROR RESUMING GRAPH:", e)
        traceback.print_exc()

    return {"status": "resumed"}