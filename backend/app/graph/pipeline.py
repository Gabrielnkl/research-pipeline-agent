# [ ] Graph definition (graph/pipeline.py):
# Wire nodes: orchestrator → web_search → summarizer → fact_checker → report_writer
# Add conditional edge after fact_checker: 
# if confidence_score < 0.7 OR len(flagged_claims) > 0 → route to HITL node (stub for now), else → report_writer

from langgraph.graph import StateGraph, END

from graph.state import AgentState

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
# Node wrappers (important)
# -------------------------

async def orchestrator_node(state: AgentState):
    subtasks = await orchestrator.plan(state)
    return {"subtasks": subtasks}


async def web_search_node(state: AgentState):
    findings = await web_search.perform_search(state)
    return {"findings": findings}


async def summarizer_node(state: AgentState):
    summaries = await summarizer.summarize_findings(state)
    return {"summaries": summaries}


async def fact_checker_node(state: AgentState):
    fact_check = await fact_checker.check_facts(state)
    return {"fact_check": fact_check}


async def report_writer_node(state: AgentState):
    report = await report_writer.write_report(state)
    return {"report": report}


# Stub for Human-in-the-loop
async def hitl_node(state: AgentState):
    # For now just pass through (later you can add approval UI)
    print("⚠️ Routing to HITL (stub)")
    return state


# -------------------------
# Conditional routing logic
# -------------------------

def route_after_fact_check(state: AgentState):
    fc = state.get("fact_check", {})

    confidence = fc.get("confidence_score", 1.0)
    flagged = fc.get("flagged_claims", [])

    if confidence < 0.7 or len(flagged) > 0:
        return "hitl"
    return "report_writer"


# -------------------------
# Build Graph
# -------------------------

def build_graph():
    builder = StateGraph(AgentState)

    # Add nodes
    builder.add_node("orchestrator", orchestrator_node)
    builder.add_node("web_search", web_search_node)
    builder.add_node("summarizer", summarizer_node)
    builder.add_node("fact_checker", fact_checker_node)
    builder.add_node("report_writer", report_writer_node)
    builder.add_node("hitl", hitl_node)

    # Entry point
    builder.set_entry_point("orchestrator")

    # Linear flow
    builder.add_edge("orchestrator", "web_search")
    builder.add_edge("web_search", "summarizer")
    builder.add_edge("summarizer", "fact_checker")

    # Conditional edge
    builder.add_conditional_edges(
        "fact_checker",
        route_after_fact_check,
        {
            "hitl": "hitl",
            "report_writer": "report_writer",
        }
    )

    # Final edges
    builder.add_edge("hitl", "report_writer")
    builder.add_edge("report_writer", END)

    return builder.compile()