from typing import List
from pydantic import BaseModel, Field
from langchain.agents import create_agent
from app.graph.state import AgentState

class FactCheckerOutput(BaseModel):
    confidence_score: float = Field(description="A score between 0.0 and 1.0 indicating the overall reliability of the information.")
    flagged_claims: List[str] = Field(description="A list of specific claims from the summaries that could not be verified.")

class FactCheckerAgent:
    def __init__(self):
        self.agent = create_agent(
            model="gpt-4o-mini",
            response_format=FactCheckerOutput
        )
    
    async def fact_check(self, state: AgentState) -> AgentState:
        all_summaries = "\n\n".join([f"{subtask}: {summary}" for subtask, summary in state["findings"].items()])
        prompt = f"Review the following summaries and assign a confidence score (0.0–1.0) for the overall reliability of the information. "\
                 f"Also, list any specific claims that you cannot verify:\n\n{all_summaries}"
        result = await self.agent.ainvoke({
            "messages": [{ "role": "user", "content": prompt }]
        })
        structured = result["structured_response"]
        state["confidence_score"] = float(structured.confidence_score)
        state["flagged_claims"] = structured.flagged_claims
        print(f"Confidence Score: {state['confidence_score']}")
        print(f"Flagged Claims: {state['flagged_claims']}")
        return state