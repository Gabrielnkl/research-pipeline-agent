import json
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from app.graph.state import AgentState


class ReportWriterAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

        self.prompt = ChatPromptTemplate.from_messages([
            ("system",
             "You are an expert research assistant tasked with synthesizing research findings into a structured markdown report."),

            ("human", "Research question: {question}"),
            ("human", "Subtasks: {subtasks}"),
            ("human", "Summarized findings: {summarized_findings}"),
            ("human", "Flagged claims: {flagged_claims}"),
            ("human", "Confidence score: {confidence_score}"),

            ("human",
             "Write a comprehensive report with the following sections:\n"
             "1. Executive Summary (2-3 sentences)\n"
             "2. Findings by Subtask\n"
             "3. Flagged Claims\n"
             "4. Sources")
        ])

    async def write_report(self, state: AgentState) -> str:

        # -------------------------
        # SAFE STATE ACCESS
        # -------------------------
        summarized_findings = (
            state.get("summarized_findings")
            or state.get("summaries")
            or state.get("findings")
            or {}
        )

        flagged_claims = state.get("flagged_claims", [])
        confidence_score = state.get("confidence_score", 1.0)

        # -------------------------
        # PROMPT
        # -------------------------
        messages = self.prompt.format_messages(
            question=state.get("question", ""),
            subtasks=json.dumps(state.get("subtasks", [])),
            summarized_findings=json.dumps(summarized_findings),
            flagged_claims=json.dumps(flagged_claims),
            confidence_score=confidence_score,
        )

        response = await self.llm.ainvoke(messages)

        return response.content.strip()