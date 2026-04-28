from typing import List
from pydantic import BaseModel, Field
from langchain.agents import create_agent
from app.graph.state import AgentState


class ReportWriterAgentOutput(BaseModel):
    subtasks: List[str] = Field(description="A list where the first item is the final markdown report synthesizing all findings. "
    "The report should include sections for Executive Summary, Findings by Subtask, Flagged Claims, and Sources.")


class ReportWriterAgent:
    def __init__(self):
        self.agent = create_agent(
            model="gpt-4o-mini",
            response_format=ReportWriterAgentOutput
        )
    
    async def write_report(self, state: AgentState) -> AgentState:
        findings_section = "\n\n".join([f"### {subtask}\n{summary}" for subtask, summary in state["findings"].items()])
        flagged_claims_section = "\n".join([f"- {claim}" for claim in state["flagged_claims"]])
        
        prompt = f"Write a structured markdown report based on the following information:\n\n"  \
                 f"**Executive Summary:**\nA brief overview of the health benefits of green tea.\n\n" \
                 f"**Findings by Subtask:**\n{findings_section}\n\n" \
                 f"**Flagged Claims:**\n{flagged_claims_section}\n\n" \
                 f"**Sources:**\nList the sources used for the findings."
        result = await self.agent.ainvoke({
            "messages": [{ "role": "user", "content": prompt }]
        })
        report = result["structured_response"].subtasks[0]  # ✅ correct
        state["report"] = report  # Assuming the report is returned in the first subtask slot
        print(f"Final Report:\n{state['report']}")
        return state