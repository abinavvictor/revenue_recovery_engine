import operator
from typing import Annotated, TypedDict, Union
from langgraph.graph import StateGraph, END
from src.agents.investigator import investigator_node
from src.agents.auditor import auditor_node
from src.agents.refund import refund_node
from src.agents.notifier import notifier_node
from src.state import DisputeState

def route_after_auditor(state: DisputeState):
    status = state.get("resolution_status")
    retries = state.get("retry_count", 0)

    #Essentially using circuit breaker for self correcting pipelines
    if status == "needs_more_info":
        if retries >= 2:
            print(" [ROUTER]: Max retries reached. Forcing Manual Review.")
            return "notifier" #retries if exceeded,it will tend to manual review
        return "investigator"

    if status == "approved":
        return "refund"

    #In all cases whether rejected,refunded or reviewed,i want notification to customer
    return "notifier"

def create_graph():
    workflow = StateGraph(DisputeState)

    
    workflow.add_node("investigator", investigator_node)
    workflow.add_node("auditor", auditor_node)
    workflow.add_node("refund", refund_node)
    workflow.add_node("notifier", notifier_node)


    workflow.set_entry_point("investigator")

    workflow.add_edge("investigator", "auditor")
    

    workflow.add_conditional_edges(
        "auditor",
        route_after_auditor,
        {
            "investigator": "investigator",
            "refund": "refund",
            "notifier": "notifier"
        }
    )

    workflow.add_edge("refund", "notifier")
    workflow.add_edge("notifier", END)

    return workflow.compile()