from typing import List
from pydantic import BaseModel, Field

from langchain.agents import create_agent

from app.graph.state import AgentState


class SubtasksOutput(BaseModel):
    subtasks: List[str] = Field(description="A list of 3-5 subtasks that break down the main research question. " \
    "Each subtask should be a concise, actionable research step.")


class OrchestratorAgent:
    def __init__(self):
        self.agent = create_agent(
            model="gpt-4o-mini",
            response_format=SubtasksOutput
        )
    
    async def plan(self, state: AgentState) -> list[str]:
        result = await self.agent.ainvoke({
            "messages": [{ "role": "user", "content": state["question"] }]
        })
        return result["structured_response"].subtasks
