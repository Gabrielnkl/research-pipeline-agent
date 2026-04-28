from langgraph.graph import StateGraph, END, START
from langgraph.types import interrupt, Command
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.graph.state import AgentState
from app.agents.orchestrator import OrchestratorAgent
from app.agents.web_search import WebSearchAgent
from app.agents.summarizer import SummarizerAgent
from app.agents.fact_checker import FactCheckerAgent
from app.agents.report_writer import ReportWriterAgent


# -------------------------
# NODES
# -------------------------

async def orchestrator(state: AgentState) -> AgentState:
    subtasks = await OrchestratorAgent().plan(state)
    state["subtasks"] = subtasks
    state["current_step"] = "orchestrator"
    return state


async def run_web_search(state: AgentState) -> AgentState:
    findings = await WebSearchAgent().run(state)
    state["findings"] = findings
    state["current_step"] = "researcher"
    return state


async def summarizer(state: AgentState) -> AgentState:
    state = await SummarizerAgent().summarize(state)
    state["current_step"] = "summarizer"
    return state


async def fact_checker(state: AgentState) -> AgentState:
    state = await FactCheckerAgent().fact_check(state)
    state["current_step"] = "fact_checker"
    return state

async def hitl(state: AgentState) -> AgentState:
    print("HITL ENTRY:", state.get("approved"))

    # ✅ Skip if already approved
    if state.get("approved") is True:
        print("✅ Skipping HITL (already approved)")
        state["approved_route"] = "proceed"
        return state

    needs_review = (
        state["confidence_score"] < 0.7
        or len(state["flagged_claims"]) > 0
    )

    if needs_review:
        is_approved = interrupt({
            "question": "Do you want to proceed with this report?",
            "details": state["flagged_claims"],
            "confidence_score": state["confidence_score"],
        })

        # 🔥 THIS LINE FIXES EVERYTHING
        state["approved"] = is_approved

        state["approved_route"] = "proceed" if is_approved else "cancel"

    else:
        state["approved"] = True
        state["approved_route"] = "proceed"

    return state

async def report_writer(state: AgentState) -> AgentState:
    state = await ReportWriterAgent().write_report(state)
    state["current_step"] = "report_writer"
    return state


async def cancelled(state: AgentState) -> AgentState:
    print(f"❌ Job {state['job_id']} was cancelled by the reviewer.")
    state["current_step"] = "cancelled"
    return state


# -------------------------
# ROUTING
# -------------------------

def route_after_hitl(state: AgentState) -> str:
    return state.get("approved_route", "proceed")


# -------------------------
# GRAPH BUILDER
# ✅ Called once at startup in main.py lifespan with a live checkpointer
# -------------------------

def build_graph(checkpointer: AsyncPostgresSaver):
    graph = (
        StateGraph(AgentState)
        .add_node("orchestrator", orchestrator)
        .add_node("researcher", run_web_search)
        .add_node("summarizer", summarizer)
        .add_node("fact_checker", fact_checker)
        .add_node("hitl", hitl)
        .add_node("report_writer", report_writer)
        .add_node("cancelled", cancelled)
        .add_edge(START, "orchestrator")
        .add_edge("orchestrator", "researcher")
        .add_edge("researcher", "summarizer")
        .add_edge("summarizer", "fact_checker")
        .add_edge("fact_checker", "hitl")
        .add_conditional_edges(
            "hitl",
            route_after_hitl,
            {
                "proceed": "report_writer",
                "cancel": "cancelled",
            }
        )
        .add_edge("report_writer", END)
        .add_edge("cancelled", END)
        .compile(checkpointer=checkpointer)
    )
    return graph


# -------------------------
# ENTRY POINT
# -------------------------

async def run_pipeline(graph, question: str, job_id: str) -> dict:
    initial_state = {
        "job_id": job_id,
        "question": question,
        "subtasks": [],
        "findings": {},
        "flagged_claims": [],
        "human_feedback": None,
        "report": None,
        "current_step": "start",
        "confidence_score": 0.0,
        "approved": None,
        "approved_route": None,
        "retry_count": 0,
    }
    config = {"configurable": {"thread_id": job_id}}
    final_state = await graph.ainvoke(initial_state, config)
    return final_state