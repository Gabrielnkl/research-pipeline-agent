from app.graph.state import AgentState

from typing import Dict, Any
from langchain_community.tools import DuckDuckGoSearchResults


class WebSearchAgent:
    def __init__(self, max_results: int = 5):
        self.search_tool = DuckDuckGoSearchResults(output_format="list")
        self.max_results = max_results

    async def run(self, state: AgentState) -> dict:
        findings: Dict[str, Any] = {}

        subtasks = state.get("subtasks", [])

        if not isinstance(subtasks, list):
            raise ValueError(f"subtasks must be a list, got {type(subtasks)}")

        for subtask in subtasks:
            try:
                query = str(subtask)

                results = await self.search_tool.ainvoke(query)  # ✅ await first
                results = results[:self.max_results]              # ✅ then slice

                structured = {
                    item["link"]: {
                        "title": item.get("title", ""),
                        "snippet": item.get("snippet", ""),
                        "source": "duckduckgo"
                    }
                    for item in results
                    if "link" in item
                }

                findings[query] = structured

            except Exception as e:
                findings[str(subtask)] = {
                    "error": str(e),
                    "results": {}
                }

        return findings