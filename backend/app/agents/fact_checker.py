# [ ] Fact Checker agent (agents/fact_checker.py):
# Review all summaries, assign a confidence_score (0.0–1.0)
# Populate flagged_claims with any statements it cannot verify

import json
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from graph.state import AgentState

class FactCheckerAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert fact checker. Your task is to review the summaries of research findings for each subtask and evaluate their reliability."),
            ("human", "Here are the summaries for each subtask: {summarized_findings}"),
            ("human", "For each subtask, identify any claims that cannot be verified based on the provided summaries. "
                      "Assign an overall confidence score between 0.0 (completely unreliable) and 1.0 (completely reliable) for the entire set of findings. "
                      "Return a JSON object with two keys: 'flagged_claims' (a list of unverified claims) and 'confidence_score' (a float).")
        ])
    
    async def check_facts(self, state: AgentState) -> dict:
        messages = self.prompt.format_messages(
            summarized_findings=json.dumps(state["findings"])
        )

        response = await self.llm.ainvoke(messages)

        try:
            result = json.loads(response.content)
            if "flagged_claims" in result and "confidence_score" in result:
                return {
                    "flagged_claims": result["flagged_claims"],
                    "confidence_score": result["confidence_score"]
                }
            else:
                raise ValueError("LLM output missing required keys")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON from LLM:\n{response.content}")