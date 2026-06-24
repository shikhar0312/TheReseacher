import operator
from typing import Annotated, TypedDict, List, Dict

class ResearchState(TypedDict):
    main_task: str
    
    # Use Annotated and operator.add so findings from multiple research passes accumulate
    research_findings: Annotated[List[Dict[str, str]], operator.add]
    
    draft: str
    
    # citations map citation number (str/int) to {"url": str, "title": str}
    citations: Dict[str, Dict[str, str]]
    
    critique_notes: str
    revision_number: int
    next_step: str
    reasoning: str  # Added reasoning field to hold the supervisor's thought process
