import json
from pydantic import BaseModel, Field
from typing import Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from app.state import ResearchState
from app.prompts import WRITER_PROMPT

class CitationDict(BaseModel):
    url: str
    title: str

class WriterOutput(BaseModel):
    draft: str = Field(description="The full markdown formatted draft report including inline citation markers like [1].")
    citations: Dict[str, CitationDict] = Field(description="A dictionary mapping citation numbers (as strings, e.g., '1') to their source URL and title.")

def writer_node(state: ResearchState):
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    structured_llm = llm.with_structured_output(WriterOutput)

    # Format findings into a string with clear indices
    findings = state.get("research_findings", [])
    findings_str = ""
    for i, finding in enumerate(findings):
        # 1-indexed for the writer's convenience
        findings_str += f"Finding {i+1}:\n"
        findings_str += f"Source URL: {finding['source_url']}\n"
        findings_str += f"Source Title: {finding.get('source_title', 'Source')}\n"
        findings_str += f"Content: {finding['content']}\n\n"

    prompt = WRITER_PROMPT.format(
        main_task=state["main_task"],
        findings_str=findings_str,
        critique_notes=state.get("critique_notes", "")
    )

    try:
        result = structured_llm.invoke(prompt)
        
        # Format the citations dictionary
        citations_dict = {
            str(k): {"url": v.url, "title": v.title}
            for k, v in result.citations.items()
        }
        
        return {
            "draft": result.draft,
            "citations": citations_dict,
            "reasoning": f"Wrote/revised draft using {len(citations_dict)} citations."
        }
    except Exception as e:
        print(f"Writer LLM call failed: {e}")
        return {
            "draft": state.get("draft", "") + f"\n\n[Writer Error: {str(e)}]",
            "reasoning": "Failed to write draft due to API error."
        }
