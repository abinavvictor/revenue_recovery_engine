def test_full_graph_execution(app):
    initial_input = {
        "order_id": "ORD-101",
        "user_claim": "I never got it!",
        "history": [],
        "shipping_status": "",
        "is_contradiction": False,
        "resolution_status": "pending"
    }
    
    
    final_state = app.invoke(initial_input)
    
    
    assert "shipping_status" in final_state
    assert len(final_state["history"]) >= 2