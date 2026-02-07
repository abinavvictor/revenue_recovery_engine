import os
import json
from langchain_community.tools.tavily_search import TavilySearchResults
from dotenv import load_dotenv

load_dotenv()

def _get_db_path():
    
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base_dir, "data", "mockdb.json")

def get_shipping_evidence(tracking_number: str) -> str:
    """Fetches real-time tracking data using Tavily."""
    try:
        search = TavilySearchResults(k=2)
        query = f"official carrier tracking status for {tracking_number}"
        results = search.invoke({"query": query})
        
        print(f" Evidence Harvested: {tracking_number}")
        return str(results)
    except Exception:
        print(f" Search Failed: {tracking_number}")
        return "Error: Could not retrieve live shipping data."

def get_internal_order_data(order_id: str) -> dict:
    
    db_path = _get_db_path()

    if not os.path.exists(db_path):
        return {"error": "Internal Database Offline"}

    with open(db_path, "r") as f:
        db = json.load(f)
        order = db.get(order_id)
        
        if order:
            print(f" Record Located: {order_id}")
            return order
        
        print(f" Record Missing: {order_id}")
        return {"error": "Order not found"}