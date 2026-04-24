#  ] Connect graph execution to job_service.py, update DB status at each node
# [ ] Run the full pipeline against a test question: "What are the main causes of inflation in 2024?"

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

        # Start the research pipeline in the background
        pipeline = ResearchPipeline()
        await pipeline.run_pipeline(question)

        return str(new_job.id)

    async def get_job_status(self, job_id: str) -> ResearchJob:
        job = await self.db_session.get(ResearchJob, job_id)
        if not job:
            raise ValueError("Job not found")
        return job