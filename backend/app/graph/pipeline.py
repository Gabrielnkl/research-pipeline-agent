from langgraph.graph import StateGraph, END
from langgraph.types import interrupt

from graph.state import AgentState
from graph.checkpointer import get_checkpointer

# Agents
from agents.orchestrator import OrchestratorAgent
from agents.web_search import WebSearchAgent
from agents.summarizer import SummarizerAgent
from agents.fact_checker import FactCheckerAgent
from agents.report_writer import ReportWriterAgent


# Instantiate agents
orchestrator = OrchestratorAgent()
web_search = WebSearchAgent()
summarizer = SummarizerAgent()
fact_checker = FactCheckerAgent()
report_writer = ReportWriterAgent()


# -------------------------
# Nodes
# -------------------------

async def orchestrator_node(state: AgentState):
    return {"subtasks": await orchestrator.plan(state)}


async def web_search_node(state: AgentState):
    question = state["question"]

    if state.get("human_feedback"):
        question += f"\nUser feedback: {state['human_feedback']}"

    findings = await web_search.perform_search({
        **state,
        "question": question
    })

    return {"findings": findings}


async def summarizer_node(state: AgentState):
    return {"summaries": await summarizer.summarize_findings(state)}


async def fact_checker_node(state: AgentState):
    return {"fact_check": await fact_checker.check_facts(state)}


async def report_writer_node(state: AgentState):
    return {"report": await report_writer.write_report(state)}


# -------------------------
# HITL Node
# -------------------------

async def hitl_node(state: AgentState):
    return interrupt({
        "flagged_claims": state.get("fact_check", {}).get("flagged_claims", []),
        "confidence_score": state.get("fact_check", {}).get("confidence_score", 1.0),
        "summaries": state.get("summaries", {}),
    })


# -------------------------
# Routing
# -------------------------

def route_after_fact_check(state: AgentState):
    fc = state.get("fact_check", {})

    if fc.get("confidence_score", 1.0) < 0.7 or len(fc.get("flagged_claims", [])) > 0:
        return "hitl"

    return "report_writer"


def route_after_hitl(state: AgentState):
    if state.get("approved", False):
        return "report_writer"

    retry_count = state.get("retry_count", 0)

    if retry_count >= 2:
        return "report_writer"

    return "web_search"


# -------------------------
# Build Graph
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
        {
            "hitl": "hitl",
            "report_writer": "report_writer",
        }
    )

    builder.add_conditional_edges(
        "hitl",
        route_after_hitl,
        {
            "report_writer": "report_writer",
            "web_search": "web_search",
        }
    )

    builder.add_edge("report_writer", END)

    from graph.checkpointer import get_checkpointer

    with get_checkpointer() as checkpointer:
        return builder.compile(checkpointer=checkpointer)
    

graph = build_graph()


class ResearchPipeline:
    async def run_pipeline(self, question: str, job_id: str):
        await graph.ainvoke(
            {
                "question": question,
                "job_id": job_id,
                "retry_count": 0,
            },
            config={
                "configurable": {
                    "thread_id": job_id
                }
            }
        )