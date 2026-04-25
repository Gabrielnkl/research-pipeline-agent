import asyncio
from langgraph.graph import StateGraph, END
from langgraph.types import interrupt

from app.graph.state import AgentState
#from app.graph.checkpointer import get_checkpointer

from app.agents.orchestrator import OrchestratorAgent
from app.agents.web_search import WebSearchAgent
from app.agents.summarizer import SummarizerAgent
from app.agents.fact_checker import FactCheckerAgent
from app.agents.report_writer import ReportWriterAgent

from app.db.postgres import AsyncSessionLocal
from app.db.utils import update_job
from app.graph.utils import update_steps


orchestrator = OrchestratorAgent()
web_search = WebSearchAgent()
summarizer = SummarizerAgent()
fact_checker = FactCheckerAgent()
report_writer = ReportWriterAgent()


# -------------------------
# NODES
# -------------------------

async def orchestrator_node(state: AgentState, config):
    print("RUNNING NODE: orchestrator")
    job_id = config["configurable"]["job_id"]

    async with AsyncSessionLocal() as db:
        steps = update_steps(state.get("subtasks"), "Orchestrator", "running")
        await update_job(db, job_id, status="running", subtasks=steps)

    subtasks = await orchestrator.plan(state)

    async with AsyncSessionLocal() as db:
        steps = update_steps(steps, "Orchestrator", "complete")
        await update_job(db, job_id, subtasks=steps)

    return {"subtasks": steps}


async def web_search_node(state: AgentState, config):
    print("RUNNING NODE: web_search")
    job_id = config["configurable"]["job_id"]

    async with AsyncSessionLocal() as db:
        steps = update_steps(state.get("subtasks"), "Web Search", "running")
        await update_job(db, job_id, subtasks=steps)

    findings = await web_search.perform_search(state)

    async with AsyncSessionLocal() as db:
        steps = update_steps(steps, "Web Search", "complete")
        await update_job(db, job_id, findings=findings, subtasks=steps)

    return {"findings": findings, "subtasks": steps}



async def summarizer_node(state: AgentState, config):
    print("RUNNING NODE: summarizer")
    job_id = config["configurable"]["job_id"]

    async with AsyncSessionLocal() as db:
        steps = update_steps(state.get("subtasks"), "Summarizer", "running")
        await update_job(db, job_id, subtasks=steps)

    summaries = await summarizer.summarize_findings(state)

    async with AsyncSessionLocal() as db:
        steps = update_steps(steps, "Summarizer", "complete")
        await update_job(db, job_id, subtasks=steps)

    return {"summaries": summaries, "subtasks": steps}


async def fact_checker_node(state: AgentState, config):
    job_id = config["configurable"]["job_id"]
    print("RUNNING NODE: fact_checker")

    async with AsyncSessionLocal() as db:
        steps = update_steps(state.get("subtasks"), "Fact Checker", "running")
        await update_job(db, job_id, subtasks=steps)

    result = await fact_checker.check_facts(state)

    async with AsyncSessionLocal() as db:
        steps = update_steps(steps, "Fact Checker", "complete")

        if result.get("flagged_claims"):
            await update_job(
                db,
                job_id,
                status="awaiting_review",
                subtasks=steps
            )
        else:
            await update_job(db, job_id, subtasks=steps)

    return {"fact_check": result, "subtasks": steps}


async def report_writer_node(state: AgentState, config):
    job_id = config["configurable"]["job_id"]
    print("RUNNING NODE: report_writer")

    async with AsyncSessionLocal() as db:
        steps = update_steps(state.get("subtasks"), "Report Writer", "running")
        await update_job(db, job_id, subtasks=steps)

    report = await report_writer.write_report(state)

    async with AsyncSessionLocal() as db:
        steps = update_steps(steps, "Report Writer", "complete")
        await update_job(
            db,
            job_id,
            status="complete",
            report=report,
            subtasks=steps
        )

    return {"report": report}


# -------------------------
# HITL
# -------------------------

async def hitl_node(state: AgentState):
    print("RUNNING NODE: hitl")
    return interrupt({
        "flagged_claims": state.get("fact_check", {}).get("flagged_claims", []),
        "summaries": state.get("summaries", {}),
    })


def route_after_fact_check(state: AgentState):
    if state.get("fact_check", {}).get("flagged_claims"):
        return "hitl"
    return "report_writer"


def route_after_hitl(state: AgentState):
    if state.get("approved"):
        return "report_writer"
    return "web_search"


# -------------------------
# GRAPH
# -------------------------

def build_graph():
    builder = StateGraph(AgentState)

    builder.add_node("orchestrator", orchestrator_node)
    builder.add_node("web_search", web_search_node)
    builder.add_node("summarizer", summarizer_node)
    builder.add_node("fact_checker", fact_checker_node)
    builder.add_node("hitl", hitl_node)
    builder.add_node("report_writer", report_writer_node)

    builder.set_entry_point("orchestrator")

    builder.add_edge("orchestrator", "web_search")
    builder.add_edge("web_search", "summarizer")
    builder.add_edge("summarizer", "fact_checker")

    builder.add_conditional_edges(
        "fact_checker",
        route_after_fact_check,
        {"hitl": "hitl", "report_writer": "report_writer"}
    )

    builder.add_conditional_edges(
        "hitl",
        route_after_hitl,
        {"report_writer": "report_writer", "web_search": "web_search"}
    )

    builder.add_edge("report_writer", END)

    
    return builder.compile()


graph = build_graph()


class ResearchPipeline:
    async def run_pipeline(self, question: str, job_id: str):
        print("🚀 PIPELINE STARTED", job_id)

        await graph.ainvoke(
            {
                "question": question,
                "job_id": job_id,
                "retry_count": 0,
            },
            config={
                "configurable": {
                    "thread_id": job_id,
                    "job_id": job_id,
                }
            }
        )