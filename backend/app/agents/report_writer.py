# [ ] Report Writer agent (agents/report_writer.py):
# Synthesize all findings into a structured markdown report
# Sections: Executive Summary, Findings by Subtask, Flagged Claims, Sources

import json
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from graph.state import AgentState

class ReportWriterAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert research assistant tasked with synthesizing research findings into a structured markdown report."),
            ("human", "Research question: {question}"),
            ("human", "Subtasks: {subtasks}"),
            ("human", "Summarized findings: {summarized_findings}"),
            ("human", "Flagged claims: {flagged_claims}"),
            ("human", "Confidence score: {confidence_score}"),
            ("human", "Write a comprehensive report with the following sections:\n"
                      "1. Executive Summary (2-3 sentences)\n"
                      "2. Findings by Subtask (detailed summaries for each subtask)\n"
                      "3. Flagged Claims (list any claims that were flagged as unverified)\n"
                      "4. Sources (list key sources cited in the findings)")
        ])

    async def write_report(self, state: AgentState) -> str:
        messages = self.prompt.format_messages(
            question=state["question"],
            subtasks=state["subtasks"],
            summarized_findings=json.dumps(state["summarized_findings"]),
            flagged_claims=json.dumps(state["flagged_claims"]),
            confidence_score=state["confidence_score"]
        )

        response = await self.llm.ainvoke(messages)

        return response.content.strip()