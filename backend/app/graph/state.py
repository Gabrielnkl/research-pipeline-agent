from typing import TypedDict, List, Optional

class AgentState(TypedDict):
    job_id: str
    question: str
    subtasks: List[str]            # Set by orchestrator
    findings: dict                 # keyed by subtask
    flagged_claims: List[str]      # Set by fact checker
    human_feedback: Optional[str]  # Set after HITL
    report: Optional[str]          # Final output
    current_step: str
    confidence_score: float
    
    # HITL
    human_feedback: Optional[str]
    approved: Optional[bool]
    retry_count: int