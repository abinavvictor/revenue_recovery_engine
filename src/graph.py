from langgraph.graph import StateGraph, END
from src.state import DisputeState
from src.agents.investigator import investigation_node
from src.agents.auditor import audit_node

# essentially designed this router to Self correct autonomously
def router(state: DisputeState):
    if state.get("resolution_status") == "needs_more_info":
        return "investigator"
    
    
    return "finalize"
def create_graph():
    
    workflow = StateGraph(DisputeState)

    
    workflow.add_node("investigator", investigation_node)
    workflow.add_node("auditor", audit_node)

    
    
    workflow.set_entry_point("investigator")
    workflow.add_edge("investigator", "auditor")
    workflow.add_edge("auditor", END)

    #selfcorrection starts here
    workflow.add_conditional_edges(
        "auditor",
        router,
        {
            "investigator": "investigator", 
            "finalize": END                       
        }
    )

    
    return workflow.compile()