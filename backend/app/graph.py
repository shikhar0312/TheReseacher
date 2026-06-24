from langgraph.graph import StateGraph, END
from app.state import ResearchState
from app.agents.supervisor import supervisor_node
from app.agents.researcher import researcher_node
from app.agents.writer import writer_node
from app.agents.critic import critic_node

def route_from_supervisor(state: ResearchState):
    next_step = state.get("next_step")
    if next_step == "END":
        return END
    elif next_step in ["researcher", "writer", "critic"]:
        return next_step
    else:
        # Default fallback
        return END

def create_graph():
    workflow = StateGraph(ResearchState)

    # Add nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("writer", writer_node)
    workflow.add_node("critic", critic_node)

    # Set entry point
    workflow.set_entry_point("supervisor")

    # Add conditional edges from supervisor
    workflow.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "researcher": "researcher",
            "writer": "writer",
            "critic": "critic",
            END: END
        }
    )

    # Always return to supervisor
    workflow.add_edge("researcher", "supervisor")
    workflow.add_edge("writer", "supervisor")
    workflow.add_edge("critic", "supervisor")

    # Compile the graph
    graph = workflow.compile()
    return graph
