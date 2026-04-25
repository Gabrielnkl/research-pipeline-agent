from sqlalchemy import Column, Text, Enum, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
import enum
import uuid

Base = declarative_base()

class JobStatus(enum.Enum):
    pending = "pending"
    running = "running"
    awaiting_review = "awaiting_review"
    complete = "complete"
    failed = "failed"

class ResearchJob(Base):
    __tablename__ = "research_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    question = Column(Text, nullable=False)

    status = Column(
        Enum(JobStatus, name="job_status"),
        default=JobStatus.pending,
        nullable=False
    )
    
    subtasks = Column(JSONB, nullable=True)
    findings = Column(JSONB, nullable=True)
    report = Column(Text, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now()
    )