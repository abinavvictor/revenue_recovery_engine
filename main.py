from src.graph import create_graph
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    
    app = create_graph()
    
    
    initial_state = {
        "order_id": "ORD-101",
        "user_claim": "I want a refund. My camera never arrived and I've been home all day.",
        "history": [],
        "shipping_status": "",
        "is_contradiction": False,
        "resolution_status": "pending"
    }
    
    print("\n INITIALIZING Revenue RECOVERy")
    print("="*40)
    
    
    for output in app.stream(initial_state):
        
        for node_name, state_update in output.items():
            print(f"DEBUG: Node '{node_name}' finished.")
            if "history" in state_update:
                print(f"LOG: {state_update['history'][-1]}")
    
    print("="*40)
    print("🏁 PROCESS COMPLETE")

if __name__ == "__main__":
    main()