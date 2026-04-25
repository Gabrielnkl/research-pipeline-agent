from typing import List, cast
from pydantic import BaseModel

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.graph.state import AgentState


class SubtasksOutput(BaseModel):
    subtasks: List[str]


class OrchestratorAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.2
        ).with_structured_output(SubtasksOutput)

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert research assistant."),
            ("human", "Break down the question into 3-5 subtasks."),
            ("human", "Question: {question}")
        ])

    async def plan(self, state: AgentState) -> list[str]:
        messages = self.prompt.format_messages(
            question=state["question"]
        )

        response = cast(SubtasksOutput, await self.llm.ainvoke(messages))

        return response.subtasks