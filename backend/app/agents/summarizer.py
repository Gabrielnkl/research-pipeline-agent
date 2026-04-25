# [ ] Summarizer agent (agents/summarizer.py):
# For each subtask finding, produce a 3-5 sentence summary with source citations
# Store summaries back into findings[subtask]

import json

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.graph.state import AgentState


class SummarizerAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.2
        )

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a research assistant that summarizes web findings."),
            ("human", "Subtask: {subtask}"),
            ("human", "Raw findings: {findings}"),
            ("human", "Write a 3-5 sentence summary with source citations. "
                      "If sources are unclear, still produce a useful summary. "
                      "Return only the summary text.")
        ])

    async def summarize_findings(self, state: AgentState) -> dict:
        summarized_findings = {}

        for subtask, raw_data in state["findings"].items():
            messages = self.prompt.format_messages(
                subtask=subtask,
                findings=str(raw_data)
            )

            response = await self.llm.ainvoke(messages)

            summarized_findings[subtask] = response.content.strip()

        return summarized_findings