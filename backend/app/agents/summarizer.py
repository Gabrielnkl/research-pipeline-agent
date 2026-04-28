from pydantic import BaseModel, Field
from langchain.agents import create_agent
from app.graph.state import AgentState
from typing import List

class SummarizerAgentOutput(BaseModel):
    subtasks: List[str] = Field(description="A list of summaries corresponding to each subtask. "
    "Each summary should be concise (3-5 sentences) and include source citations where applicable.")


class SummarizerAgent:
    def __init__(self):
        self.agent = create_agent(
            model="gpt-4o-mini",
            response_format=SummarizerAgentOutput
        )
    
    async def summarize(self, state: AgentState) -> AgentState:
        for subtask, raw_finding in state["findings"].items():
            prompt = f"Summarize the following search results for the subtask '{subtask}':\n\n{raw_finding}\n\n"
            
            result = await self.agent.ainvoke({
                "messages": [{ "role": "user", "content": prompt }]
            })
            
            structured = result["structured_response"]
            summary = structured.subtasks[0]  # ✅ correct

            print(f"Summary for '{subtask}': {summary}")

            state["findings"][subtask] = summary
        return state