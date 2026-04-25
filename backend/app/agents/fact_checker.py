import json
import re
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from app.graph.state import AgentState


def extract_json(text: str) -> dict:
    """
    Robustly extract a JSON object from LLM output that may be:
    - Raw JSON
    - Wrapped in ```json ... ```  or  ``` ... ```
    - Preceded / followed by explanation text
    """
    if not text or not text.strip():
        raise ValueError("LLM returned an empty response")

    text = text.strip()

    # 1. Try direct parse first (already clean JSON)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 2. Strip markdown code fences — ```json { ... } ``` or ``` { ... } ```
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence_match:
        try:
            return json.loads(fence_match.group(1))
        except json.JSONDecodeError:
            pass

    # 3. Find the first { ... } block anywhere in the string
    brace_match = re.search(r"\{.*\}", text, re.DOTALL)
    if brace_match:
        try:
            return json.loads(brace_match.group())
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Could not extract valid JSON from LLM response:\n{text}")


class FactCheckerAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

        self.prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "You are an expert fact checker. Review the research summaries provided "
                "and evaluate their reliability.\n\n"
                "IMPORTANT: Your entire response must be a single raw JSON object. "
                "Do NOT use markdown, code fences, or any text outside the JSON object.",
            ),
            (
                "human",
                "Here are the summaries for each subtask:\n{summarized_findings}\n\n"
                "Identify any claims that cannot be verified from the provided summaries. "
                "Assign an overall confidence score between 0.0 (completely unreliable) "
                "and 1.0 (completely reliable) for the entire set of findings.\n\n"
                "Respond with ONLY this JSON structure, nothing else:\n"
                '{{"flagged_claims": ["claim 1", "claim 2"], "confidence_score": 0.85}}',
            ),
        ])

    async def check_facts(self, state: AgentState) -> dict:
        messages = self.prompt.format_messages(
            summarized_findings=json.dumps(state["findings"], indent=2)
        )

        response = await self.llm.ainvoke(messages)

        try:
            result = extract_json(response.content)
        except ValueError as e:
            raise ValueError(str(e))

        # Validate and coerce — never crash on a missing/wrong-typed key
        flagged_claims = result.get("flagged_claims")
        confidence_score = result.get("confidence_score")

        if not isinstance(flagged_claims, list):
            flagged_claims = []

        if not isinstance(confidence_score, (int, float)):
            try:
                confidence_score = float(confidence_score)
            except (TypeError, ValueError):
                confidence_score = 0.0

        # Clamp to [0.0, 1.0]
        confidence_score = max(0.0, min(1.0, float(confidence_score)))

        return {
            "flagged_claims": flagged_claims,
            "confidence_score": confidence_score,
        }