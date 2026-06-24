from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from app.state import ResearchState
from app.prompts import SUPERVISOR_PROMPT

class SupervisorDecision(BaseModel):
    next_step: str = Field(description="The next agent to run: 'researcher', 'writer', 'critic', or 'END'")
    reasoning: str = Field(description="A detailed explanation of why this decision was made")

def supervisor_node(state: ResearchState):
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    structured_llm = llm.with_structured_output(SupervisorDecision)

    draft_exists = bool(state.get("draft"))
    critique_exists = bool(state.get("critique_notes"))
    findings_count = len(state.get("research_findings", []))
    revision_number = state.get("revision_number", 0)

    prompt = SUPERVISOR_PROMPT.format(
        main_task=state["main_task"],
        findings_count=findings_count,
        draft_exists=draft_exists,
        critique_exists=critique_exists,
        revision_number=revision_number
    )

    try:
        decision = structured_llm.invoke(prompt)
        # Ensure we cap revisions
        if revision_number >= 3 and decision.next_step != "END":
            decision.next_step = "END"
            decision.reasoning += " (Forced END due to maximum revision limit reached)."
            
        return {
            "next_step": decision.next_step,
            "reasoning": decision.reasoning
        }
    except Exception as e:
        # Fallback in case of API failure or parsing issue
        print(f"Supervisor LLM call failed: {e}")
        return {
            "next_step": "researcher" if findings_count == 0 else "END",
            "reasoning": f"Fallback routing due to API error: {str(e)}"
        }
