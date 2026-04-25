import asyncio
import uuid

from db.models import ResearchJob, JobStatus
from graph.pipeline import ResearchPipeline


class JobService:
    def __init__(self, db_session):
        self.db_session = db_session

    async def start_job(self, question: str) -> str:
        new_job = ResearchJob(
            question=question,
            status=JobStatus.pending
        )

        self.db_session.add(new_job)
        await self.db_session.commit()
        await self.db_session.refresh(new_job)

        # Update status → running
        new_job.status = JobStatus.running
        await self.db_session.commit()

        # Start pipeline in background
        pipeline = ResearchPipeline()

        asyncio.create_task(
            pipeline.run_pipeline(
                question=question,
                job_id=str(new_job.id)
            )
        )

        return str(new_job.id)

    async def get_job_status(self, job_id: str) -> ResearchJob:
        job = await self.db_session.get(
            ResearchJob,
            uuid.UUID(job_id)
        )

        if not job:
            raise ValueError("Job not found")

        return job