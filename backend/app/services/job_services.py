import traceback
import uuid

from sqlalchemy import select
from app.db.models import ResearchJob, JobStatus
from app.db.postgres import AsyncSessionLocal
from app.graph.pipeline import run_pipeline



async def run_pipeline_safe(question: str, job_id: str, graph):
    async with AsyncSessionLocal() as session:
        try:
            print(f"🚀 Running pipeline for job {job_id}")

            result = await run_pipeline(graph, question, job_id)

            print("🧠 FINAL STATE FULL:", result)
            print("🧠 FINAL REPORT:", result.get("report"))

            job_uuid = uuid.UUID(job_id)

            db_result = await session.execute(
                select(ResearchJob).where(ResearchJob.id == job_uuid)
            )
            job = db_result.scalar_one_or_none()

            if not job:
                return

            # 🔴 HANDLE INTERRUPT
            if "__interrupt__" in result:
                print(f"⏸️ Job {job_id} awaiting review")

                job.status = JobStatus.awaiting_review
                job.subtasks = result.get("subtasks", [])
                job.findings = result.get("findings", {})
                job.report = None  # explicitly clear

                await session.commit()
                return

            # ✅ FINAL RESULT
            print(f"✅ Job {job_id} completed")

            job.status = JobStatus.complete
            job.subtasks = result.get("subtasks", [])
            job.findings = result.get("findings", {})
            job.report = result.get("report")

            await session.commit()

        except Exception as e:
            print(f"❌ Pipeline failed for job {job_id}: {e}")
            traceback.print_exc()

            job_uuid = uuid.UUID(job_id)

            db_result = await session.execute(
                select(ResearchJob).where(ResearchJob.id == job_uuid)
            )
            job = db_result.scalar_one_or_none()

            if job:
                job.status = JobStatus.failed
                await session.commit()