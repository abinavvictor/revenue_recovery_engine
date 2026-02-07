from src.state import DisputeState 
from src.tools.logistics import get_shipping_evidence, get_internal_order_data
def investigation_node(state: DisputeState):
    """
    The Fact-Finder: Retrieves internal order details and external shipping status.
    """
    print(f" INVESTIGATOR: Pulling file for Order {state['order_id']}...")

    order_info = get_internal_order_data(state["order_id"])
    
    if "error" in order_info:
        return {
            "history": [f"Investigator: Failed to find order {state['order_id']} in database."],
            "resolution_status": "manual_review"
        }

    tracking_no = order_info.get("tracking")
    item_name = order_info.get("item")
    
   
    #this i thought was cool,to construct a query with pattern, instead of just tracking number
    smart_query = f"UPS tracking status and delivery confirmation for {tracking_no}"
    
    print(f" INVESTIGATOR: Searching web for: {smart_query}...")
    
    
    actual_shipping_data = get_shipping_evidence(smart_query) 
    

    return {
        "shipping_status": str(actual_shipping_data),
        "history": [f"Investigator: Retrieved records for {item_name}. Smart-search performed for tracking."],
    }