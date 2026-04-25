import json
from typing import Dict, List

from langchain_community.tools import DuckDuckGoSearchResults

from app.graph.state import AgentState


class WebSearchAgent:
    def __init__(self):
        self.search_tool = DuckDuckGoSearchResults()

    async def perform_search(self, state: AgentState) -> Dict:
        findings = {}

        subtasks = state.get("subtasks", [])
        question = state.get("question")

        print("\n🔍 WEB SEARCH START")
        print("Question:", question)
        print("Subtasks:", subtasks)

        # If no subtasks, fallback to main question
        if not subtasks:
            subtasks = [{"id": "main", "name": question}]

        for subtask in subtasks:
            # ✅ extract string query
            query = subtask.get("name") if isinstance(subtask, dict) else str(subtask)

            print(f"🔎 Searching: {query}")

            try:
                results = self.search_tool.run({
                    "query": query
                })
            except Exception as e:
                print(f"❌ Search failed for: {query}", e)
                results = f"Error: {str(e)}"

            # ✅ use string key
            findings[query] = results

        print("✅ WEB SEARCH DONE\n")

        return findings