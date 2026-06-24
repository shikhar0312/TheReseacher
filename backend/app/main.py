import asyncio
import json
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from app.graph import create_graph

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

graph = create_graph()

class ResearchRequest(BaseModel):
    topic: str

@app.post("/api/research")
async def research_endpoint(request: ResearchRequest):
    async def event_generator():
        initial_state = {
            "main_task": request.topic,
            "research_findings": [],
            "draft": "",
            "citations": {},
            "critique_notes": "",
            "revision_number": 0,
            "next_step": ""
        }

        # Run the graph and stream events
        # We use astream_events to get granular updates from LangGraph
        async for event in graph.astream_events(initial_state, version="v2"):
            kind = event["event"]
            
            # We are interested in when nodes complete to send updates
            # Node execution completes
            if kind == "on_chat_model_stream":
                # Optionally we can stream tokens, but the spec says stream agent progress.
                # Astream_events gives on_chain_end for nodes.
                pass
                
            elif kind == "on_chain_end":
                name = event["name"]
                
                # Check if this is one of our agents
                if name in ["supervisor", "researcher", "writer", "critic"]:
                    output_state = event["data"].get("output", {})
                    # If there's an output state directly from the node
                    if isinstance(output_state, dict):
                        # Construct payload
                        payload = {
                            "agent": name,
                            "status": "completed",
                            "data": {},
                            "reasoning": output_state.get("next_step_reasoning", None) # Extracted if available
                        }
                        
                        # Add relevant data based on agent
                        if name == "researcher" and "research_findings" in output_state:
                            payload["data"]["findings_count"] = len(output_state["research_findings"])
                        elif name == "critic" and "critique_notes" in output_state:
                            payload["data"]["critique_notes"] = output_state["critique_notes"]
                            
                        # Send event
                        yield {
                            "data": json.dumps(payload)
                        }
                        
        # After graph completes, we need to send the final report.
        # However, astream_events doesn't automatically give the final state easily at the end without manual accumulation.
        # Actually, we can just use `astream` for node-level updates which might be simpler and cleaner for this requirement.
        
    # Let's use a cleaner approach with `astream` instead of `astream_events` for agent level events.
    async def node_event_generator():
        initial_state = {
            "main_task": request.topic,
            "research_findings": [],
            "draft": "",
            "citations": {},
            "critique_notes": "",
            "revision_number": 0,
            "next_step": "",
            "reasoning_log": []
        }

        final_state = None
        async for output in graph.astream(initial_state, stream_mode="updates"):
            # `output` is a dict where key is the node name, value is the state update returned by the node
            for node_name, state_update in output.items():
                payload = {
                    "agent": node_name,
                    "status": "completed",
                    "data": {},
                    "reasoning": state_update.get("reasoning", None)
                }

                if node_name == "researcher":
                    payload["data"]["new_findings"] = len(state_update.get("research_findings", []))
                elif node_name == "writer":
                    payload["data"]["draft_length"] = len(state_update.get("draft", ""))
                elif node_name == "critic":
                    payload["data"]["critique"] = state_update.get("critique_notes", "")
                
                yield {
                    "data": json.dumps(payload)
                }
                final_state = state_update # Keep track of the latest state

        # When the stream finishes, send the END event with the complete report
        # We need the full state though. astream with updates mode gives partial updates.
        # We'll use graph.ainvoke or accumulate state manually.
        pass

    # Better approach: We accumulate state manually as stream_mode="updates" yields dicts
    async def robust_event_generator():
        current_state = {
            "main_task": request.topic,
            "research_findings": [],
            "draft": "",
            "citations": {},
            "critique_notes": "",
            "revision_number": 0,
            "next_step": "",
            "reasoning": ""
        }
        
        async for output in graph.astream(current_state, stream_mode="updates"):
            for node_name, state_update in output.items():
                # Merge state manually for tracking, though LangGraph does it internally
                # For `astream` with "updates", LangGraph returns what the node *returned*, not the full state.
                
                reasoning = state_update.get("reasoning", None)
                
                payload = {
                    "agent": node_name,
                    "status": "completed",
                    "data": {},
                    "reasoning": reasoning
                }
                
                yield {
                    "data": json.dumps(payload)
                }

        # To get the final state, it's easier to run astream with stream_mode="values"
        # Let's switch to stream_mode="values" which gives the full state after each node.
        
    async def values_event_generator():
        initial_state = {
            "main_task": request.topic,
            "research_findings": [],
            "draft": "",
            "citations": {},
            "critique_notes": "",
            "revision_number": 0,
            "next_step": "",
            "reasoning": ""
        }
        
        # Keep track of who just ran. The values mode yields the state at the beginning,
        # and then after every node completes.
        # We can figure out the agent from the change in state or by tracking sequence.
        # Actually, stream_mode=["updates", "values"] is possible but complicated.
        pass
        
    # Reverting to the `updates` mode which is standard for node-level events
    async def final_generator():
        initial_state = {
            "main_task": request.topic,
            "research_findings": [],
            "draft": "",
            "citations": {},
            "critique_notes": "",
            "revision_number": 0,
            "next_step": "",
            "reasoning": ""
        }
        
        # We will use `astream` with `stream_mode="updates"` to get the specific agent updates
        # To get the final state, we can just accumulate the updates ourselves or fetch it at the end.
        
        full_state = initial_state.copy()
        
        async for output in graph.astream(initial_state, stream_mode="updates"):
            for node_name, state_update in output.items():
                # Accumulate the state manually
                if "research_findings" in state_update:
                    full_state["research_findings"].extend(state_update["research_findings"])
                if "draft" in state_update:
                    full_state["draft"] = state_update["draft"]
                if "citations" in state_update:
                    full_state["citations"] = state_update["citations"]
                if "critique_notes" in state_update:
                    full_state["critique_notes"] = state_update["critique_notes"]
                if "revision_number" in state_update:
                    full_state["revision_number"] = state_update["revision_number"]
                if "next_step" in state_update:
                    full_state["next_step"] = state_update["next_step"]
                if "reasoning" in state_update:
                    full_state["reasoning"] = state_update["reasoning"]

                payload = {
                    "agent": node_name,
                    "status": "completed",
                    "data": {},
                    "reasoning": state_update.get("reasoning", None)
                }
                
                yield {
                    "data": json.dumps(payload)
                }
                
        # Finally, emit the END event
        final_payload = {
            "agent": "system",
            "status": "final",
            "data": {
                "draft": full_state["draft"],
                "citations": full_state["citations"]
            },
            "reasoning": "Research complete."
        }
        yield {
            "data": json.dumps(final_payload)
        }

    return EventSourceResponse(final_generator())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
