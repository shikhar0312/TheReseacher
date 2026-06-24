from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from app.state import ResearchState
from app.prompts import CRITIC_PROMPT

class CriticOutput(BaseModel):
    decision: str = Field(description="Must be either 'APPROVED' or 'REVISE'")
    feedback: str = Field(description="Specific, actionable feedback notes if decision is 'REVISE'. If 'APPROVED', leave empty or say 'Draft is approved.'")

def critic_node(state: ResearchState):
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0)
    structured_llm = llm.with_structured_output(CriticOutput)

    # We provide the draft and citations to the critic
    draft = state.get("draft", "")
    
    prompt = CRITIC_PROMPT.format(
        main_task=state["main_task"]
    )
    prompt += f"\n\nDraft Report to Review:\n{draft}"

    try:
        result = structured_llm.invoke(prompt)
        
        notes = result.feedback if result.decision == "REVISE" else ""
        current_revision = state.get("revision_number", 0)
        
        return {
            "critique_notes": notes,
            "revision_number": current_revision + 1,
            "reasoning": f"Critic decision: {result.decision}. Notes: {notes[:100]}..." if notes else "Critic approved the draft."
        }
    except Exception as e:
        print(f"Critic LLM call failed: {e}")
        return {
            "critique_notes": f"Critic error: {str(e)}",
            "revision_number": state.get("revision_number", 0) + 1,
            "reasoning": "Critic failed due to API error."
        }
