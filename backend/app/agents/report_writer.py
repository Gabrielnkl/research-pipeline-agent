from typing import List
from pydantic import BaseModel, Field
from langchain.agents import create_agent
from app.graph.state import AgentState


class ReportWriterAgentOutput(BaseModel):
    report: str = Field(description="Final markdown report")


class ReportWriterAgent:
    def __init__(self):
        self.agent = create_agent(
            model="gpt-4o-mini",
            response_format=ReportWriterAgentOutput
        )
    
    async def write_report(self, state: AgentState) -> AgentState:
        findings_section = "\n\n".join([
            f"### {subtask}\n{summary}"
            for subtask, summary in state["findings"].items()
        ])

        flagged_claims_section = "\n".join([
            f"- {claim}" for claim in state["flagged_claims"]
        ])

        question = state.get("question", "")

        prompt = f"""
                Write a structured markdown report.

                ## Question
                {question}

                ## Findings by Subtask
                {findings_section}

                ## Flagged Claims
                {flagged_claims_section}

                ## Instructions
                - Include Executive Summary
                - Include Findings per subtask
                - Include flagged claims
                - Include sources
                """

        result = await self.agent.ainvoke({
            "messages": [{"role": "user", "content": prompt}]
        })

        report = result["structured_response"].report

        print("🧠 GENERATED REPORT:", report[:200])

        return {
            **state,
            "report": report
        }