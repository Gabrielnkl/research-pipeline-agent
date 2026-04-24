# [ ] Web Search agent (agents/web_search.py):
# Use langchain_community.tools.TavilySearch or DuckDuckGoSearchRun
# For each subtask, run a search and store raw results in findings[subtask]

import json

from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchResults

from graph.state import AgentState


class WebSearchAgent:
    def __init__(self):
        self.search_tool = DuckDuckGoSearchResults()
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert research assistant."),
            ("human", "Research question: {question}"),
            ("human", "Subtasks: {subtasks}"),
            ("human", "Raw search findings: {findings}"),
            ("human", "Summarize the findings for each subtask. Return a JSON where each key is a subtask and value is a clean summary.")
        ])

    async def perform_search(self, state: AgentState) -> dict:
        findings = {}

        # Step 1: Run searches
        for subtask in state["subtasks"]:
            search_results = self.search_tool.run(subtask)
            findings[subtask] = search_results

        # Step 2: Format prompt with real data
        messages = self.prompt.format_messages(
            question=state["question"],
            subtasks=state["subtasks"],
            findings=json.dumps(findings)
        )

        # Step 3: Call LLM
        response = await self.llm.ainvoke(messages)

        # Step 4: Parse JSON safely
        try:
            summarized = json.loads(response.content)
            if isinstance(summarized, dict):
                return summarized
            else:
                raise ValueError("LLM output is not a dict")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON from LLM:\n{response.content}")