from typing import TypedDict, List, Optional

class AgentState(TypedDict):
    job_id: str
    question: str
    subtasks: List[str]           # Set by orchestrator
    findings: dict                # Keyed by subtask, updated by summarizer
    flagged_claims: List[str]     # Set by fact_checker
    report: Optional[str]         # Final output, set by report_writer
    current_step: str             # Tracks progress through the pipeline

    confidence_score: float       # Set by fact_checker (0.0 to 1.0)

    # HITL
    human_feedback: Optional[str]
    approved: Optional[bool]
    approved_route: Optional[str] # ✅ "proceed" or "cancel" — used by route_after_hitl

    retry_count: int