import asyncio
from langgraph.graph import StateGraph, END
from langgraph.types import interrupt

from app.graph.state import AgentState

from app.agents.orchestrator import OrchestratorAgent
from app.agents.web_search import WebSearchAgent
from app.agents.summarizer import SummarizerAgent
from app.agents.fact_checker import FactCheckerAgent
from app.agents.report_writer import ReportWriterAgent
from app.graph.checkpointer import checkpointer

from typing import Literal
from langgraph.types import interrupt, Command
from langgraph.graph import START, END, StateGraph


# orchestrator = OrchestratorAgent()
# web_search = WebSearchAgent()
# summarizer = SummarizerAgent()
# fact_checker = FactCheckerAgent()
# report_writer = ReportWriterAgent()


# -------------------------
# NODES
# -------------------------

def orchestrator(state: AgentState) -> AgentState:
    if state["current_step"] == START:
        subtasks = OrchestratorAgent().plan(state)
        state["subtasks"] = subtasks
        state["current_step"] = "orchestrator"
    return state

def run_web_search(state: AgentState) -> AgentState:
    if state["current_step"] == "orchestrator":
        agent = WebSearchAgent()
        findings = agent.run(state)

        state["findings"] = findings
        state["current_step"] = "researcher"

    return state


def summarizer(state: AgentState) -> AgentState:
    if state["current_step"] == "researcher":  # ✅ FIX
        state = SummarizerAgent().summarize(state)
        state["current_step"] = "summarizer"
    return state


def fact_checker(state: AgentState) -> AgentState:
    if state["current_step"] == "summarizer":
        state = FactCheckerAgent().fact_check(state)
        state["current_step"] = "fact_checker"
    return state

def hitl(state: AgentState) -> Command[Literal["proceed", "cancel"]]:
    if state["current_step"] == "fact_checker" and (state["confidence_score"] < 0.7 or len(state["flagged_claims"]) > 0):
        is_approved = interrupt({
        "question": "Do you want to proceed with this action?",
        "details": state["flagged_claims"]
        })
        if is_approved:
            return Command(goto="proceed")  # Runs after the resume payload is provided
        else:
            return Command(goto="cancel")
    return Command(goto="proceed")  # Default to proceed if no issues


def report_writer(state: AgentState) -> AgentState:
    if state["current_step"] == "fact_checker":
        state = ReportWriterAgent().write_report(state)
        state["current_step"] = "report_writer"
    return state


graph = (
    StateGraph(AgentState)
    .add_node("orchestrator", orchestrator)
    .add_node("researcher", run_web_search)
    .add_node("summarizer", summarizer)
    .add_node("fact_checker", fact_checker)
    .add_node("hitl", hitl)
    .add_node("report_writer", report_writer)
    .add_edge(START, "orchestrator")
    .add_edge("orchestrator", "researcher")
    .add_edge("researcher", "summarizer")
    .add_edge("summarizer", "fact_checker")
    .add_edge("fact_checker", "hitl")
    .add_edge("hitl", "report_writer")
    .add_edge("report_writer", END)
    .compile(checkpointer=checkpointer)
)


async def run_pipeline(graph, question, job_id):
    initial_state = {
        "job_id": job_id,
        "question": question,
        "subtasks": [],
        "findings": {},
        "flagged_claims": [],
        "human_feedback": None,
        "report": None,
        "current_step": START,
        "confidence_score": 0.0,
        "approved": None,
        "retry_count": 0
    }
    config = {"configurable": {"thread_id": job_id}}
    final_state = await graph.ainvoke(initial_state, config)
    return final_state