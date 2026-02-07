import pytest
from src.agents.auditor import audit_node

def test_auditor_detects_contradiction():
    # Simulate a user lying
    mock_state = {
        "order_id": "ORD-101",
        "user_claim": "I never received my package!",
        "shipping_status": "Status: Delivered. Signed for by: Front Desk.",
        "history": []
    }
    
    result = audit_node(mock_state)
    
    assert result["is_contradiction"] is True
    assert result["resolution_status"] == "win_recommended"

def test_auditor_handles_honest_claim():
    # Simulate a package that is actually lost
    mock_state = {
        "order_id": "ORD-101",
        "user_claim": "Where is my stuff?",
        "shipping_status": "Status: In Transit. Delayed due to weather.",
        "history": []
    }
    
    result = audit_node(mock_state)
    
    assert result["is_contradiction"] is False
    assert result["resolution_status"] == "manual_review"