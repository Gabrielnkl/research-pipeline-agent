# [ ] Orchestrator agent (agents/orchestrator.py):
# Prompt: decompose the research question into 3-5 specific subtasks
# Output: subtasks: List[str]
# Use structured output (Pydantic) to parse cleanly

import json

from langchain import LLMChain
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from schemas.research import StartResearchRequest, JobStatusResponse
from graph.state import AgentState

class OrchestratorAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert research assistant. Your task is to break down the user's research question into 3-5 specific, actionable subtasks that will help answer the main question."),
            ("user", "Here is the research question: {question}"),
            ("assistant", "Please provide a list of 3-5 subtasks that would help answer this question. Format your response as a JSON array of strings.")
        ])

        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)

    async def generate_subtasks(self, state: AgentState) -> list[str]:
        response = await self.chain.arun({"question": state["question"]})
        # Parse the response as JSON
        try:
            subtasks = json.loads(response)
            if isinstance(subtasks, list) and all(isinstance(s, str) for s in subtasks):
                return subtasks
            else:
                raise ValueError("Response is not a valid list of strings")
        except json.JSONDecodeError:
            raise ValueError("Failed to parse LLM response as JSON")