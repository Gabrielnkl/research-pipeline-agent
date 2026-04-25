# [ ] Set up PostgreSQL checkpointer (graph/checkpointer.py) using langgraph-checkpoint-postgres
# [ ] Add HITLNode to the graph:
# Calls interrupt({"flagged_claims": state["flagged_claims"], "findings_summary": ...})
# This freezes the graph and stores state to DB
# Update job status to awaiting_review
# [ ] Create POST /research/{id}/approve endpoint:
# Accepts { approved: bool, feedback: string }
# If approved: resumes graph with feedback → continues to report_writer
# If rejected: resumes graph → loops back to web_search with feedback as additional context
# [ ] Add rejection loop edge: after HITL, if rejected → back to web_search with human_feedback injected into state
# [ ] Add maximum retry counter (e.g., 2 rejections → auto-escalate with a warning in the report)
# [ ] Test full loop: start job → wait for HITL pause → approve via API → get final report

# graph/checkpointer.py

import os
from contextlib import contextmanager
from langgraph.checkpoint.postgres import PostgresSaver


@contextmanager
def get_checkpointer():
    db_url = os.getenv("DATABASE_URL")

    if not db_url:
        raise ValueError("DATABASE_URL not set")

    with PostgresSaver.from_conn_string(db_url) as saver:
        yield saver