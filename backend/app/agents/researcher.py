from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_tavily import TavilySearch
from app.state import ResearchState
import json

def researcher_node(state: ResearchState):
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    
    # Simple query generation
    query_prompt = f"Generate 1-3 distinct specific search queries to research the following topic or address the latest critique. Topic: {state['main_task']}\nCritique notes: {state.get('critique_notes', '')}\nReturn only a JSON list of strings."
    
    try:
        query_response = llm.invoke(query_prompt)
        # Parse queries
        try:
            # Clean up potential markdown formatting from gemini
            content = query_response.content.replace("```json", "").replace("```", "").strip()
            queries = json.loads(content)
        except:
            queries = [state['main_task']]
    except Exception as e:
        queries = [state['main_task']]

    search = TavilySearch(max_results=3)
    
    new_findings = []
    
    for query in queries:
        try:
            results_dict = search.invoke(query)
            for res in results_dict.get("results", []):
                # Ask LLM to extract key points from the search result snippet
                extract_prompt = f"""
                Extract the key factual points from this text that are relevant to: {state['main_task']}.
                Text: {res['content']}
                Be concise. Output the extracted facts as a single coherent paragraph or bullet points.
                """
                extraction = llm.invoke(extract_prompt).content
                
                new_findings.append({
                    "content": extraction,
                    "source_url": res['url'],
                    "source_title": res.get('title', 'Source')
                })
        except Exception as e:
            print(f"Search failed for query '{query}': {e}")
            
    # Accumulate findings via operator.add in the state schema
    return {
        "research_findings": new_findings,
        "reasoning": f"Executed searches for queries: {', '.join(queries)} and found {len(new_findings)} results."
    }
