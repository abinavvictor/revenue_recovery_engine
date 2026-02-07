from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from src.state import DisputeState


def get_llm():
    """ 
    Pure Automatic Handshake. 
    LangChain will automatically pull GROQ_API_KEY from os.environ.
    """
    return ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

def audit_node(state: DisputeState):
    print(f"--- ⚖️ NODE: Auditor reviewing Case {state['order_id']} ---")
    
    #Guard rail logic, essentially tripping LLM with circuit
    current_retries = state.get("retry_count", 0)
    shipping_info = state.get("shipping_status", "")
    
    
    if not shipping_info or "error" in shipping_info.lower() or "none" in shipping_info.lower():
        if current_retries < 3:
            print(f"🔄 AUDITOR: Missing evidence. Triggering retry #{current_retries + 1}")
            return {
                "resolution_status": "needs_more_info",
                "retry_count": current_retries + 1,
                "history": state.get("history", []) + ["Auditor: Evidence incomplete. Retrying search."]
            }
        else:
            print(" AUDITOR: Max retries reached. Escalating to Human.")
            return {
                "resolution_status": "manual_review",
                "history": state.get("history", []) + ["Auditor: Max retries reached. No logistics data found."]
            }

    #Setting my LLM according to my rules
    system_instruction = """
You are a skeptical Fraud Investigator. Your job is to verify if a claim is 100% physically impossible.

CRITICAL CHECKLIST:
1. What is the EXACT status in the evidence? (Delivered, In-Transit, Exception, or Lost?)
2. What is the DATE of delivery? 
3. Does the tracking number in the evidence match the order?

VERDICT RULES:
- If Status == "Delivered" AND Claim == "Not Received" -> Contradiction: TRUE.
- If Status == "In-Transit" or "Delayed" -> Contradiction: FALSE (The user is right, it's not there yet).
- If Status == "Lost" or "Returned to Sender" -> Contradiction: FALSE.

Output your reasoning first, then the final verdict.
"""
    
    
    user_context = f"""
    USER CLAIM: {state.get('user_claim', 'No claim provided')}
    SHIPPING EVIDENCE: {shipping_info}
    """
    
    
    response = get_llm().invoke([
        SystemMessage(content=system_instruction),
        HumanMessage(content=user_context)
    ])
    
    #Validating if my LLM Logic i defind above caters to the setup
    claim_text = state.get("user_claim", "").lower()
    llm_verdict = response.content.lower()
    contradiction_found = "contradiction: true" in llm_verdict
    
    return {
    "is_contradiction": contradiction_found,
    "history": state.get("history", []) + [f"Auditor: Verified evidence. Result: {contradiction_found}"],
    "resolution_status": "win_recommended" if contradiction_found else "manual_review"
}