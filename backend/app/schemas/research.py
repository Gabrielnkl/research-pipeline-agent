# schemas/research.py
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from typing import Optional

class JobStatus(str, Enum):
    pending          = "pending"
    running          = "running"
    awaiting_review  = "awaiting_review"
    complete         = "complete"
    failed           = "failed"

class FindingItem(BaseModel):
    summary:    str
    sources:    list[str]
    confidence: float

# --- Requests ---

class StartResearchRequest(BaseModel):
    question: str = Field(..., min_length=10, max_length=500)

class ReviewRequest(BaseModel):
    approved: bool
    feedback: Optional[str] = None

# --- Responses ---

class StartResearchResponse(BaseModel):
    job_id: str

class JobStatusResponse(BaseModel):
    job_id:          str
    status:          JobStatus
    question:        str
    subtasks:        Optional[list[str]]        = None
    flagged_claims:  Optional[list[str]]        = None
    retry_count:     int
    updated_at:      datetime

    class Config:
        from_attributes = True  # lets you do JobStatusResponse.model_validate(db_row)

class ReportResponse(BaseModel):
    job_id:      str
    question:    str
    report:      str
    retry_count: int