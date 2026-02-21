from langchain_groq import ChatGroq
from src.state import DisputeState

async def auditor_node(state: DisputeState):
    order_id = state.get("order_id")
    history = state.get("history", [])
    retries = state.get("retry_count", 0)

    print(f"NODE: Auditor reviewing Case {order_id} (Attempt: {retries}) ---")

    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
    evidence_block = "\n".join(history) if history else "No evidence gathered."

    prompt = f"""
    Senior Chargeback Auditor is ready. Customer claims non-delivery for Order {order_id}.
    Attempt: {retries}

    EVIDENCE:
    {evidence_block}

    VERDICT RULES — based on BOTH DB status and SHIPPO_STATUS:

    1. VERDICT: rejected
       → SHIPPO_STATUS is DELIVERED (regardless of DB status)
         Carrier confirms delivery. Claim is fraudulent. Defend chargeback.
       → OR DB says Delivered AND SHIPPO_STATUS is UNKNOWN (DB alone is sufficient)

    2. VERDICT: approved
       → SHIPPO_STATUS is FAILURE or RETURNED (carrier confirms non-delivery)
         AND STRIPE_PI_ID is present. Process refund.

    3. VERDICT: manual_review
       → SHIPPO_STATUS is TRANSIT or UNKNOWN with no DB confirmation either way
         Package still moving OR evidence insufficient. Do not reject or refund yet.
       → OR STRIPE_PI_ID is MISSING
       → OR FRAUD_INDICATOR is INCONCLUSIVE
       → OR attempt >= 2 with no clear answer

    4. VERDICT: needs_more_info
       → ONLY if attempt < 1 AND both DB and Shippo have no usable data

    STRICT: TRANSIT means the package has NOT been delivered yet — 
    do NOT verdict rejected for TRANSIT. Use manual_review instead.

    First line must be exactly: VERDICT: <rejected|approved|manual_review|needs_more_info>
    Then 2 sentences reasoning citing both DB and Shippo.
    """

    response = await llm.ainvoke(prompt)
    content = response.content.lower()

    
    status = None
    for line in content.split("\n"):
        stripped = line.strip()
        if stripped.startswith("verdict:"):
            val = stripped.split(":", 1)[1].strip().replace(" ", "_")
            if val in ("approved", "rejected", "needs_more_info", "manual_review"):
                status = val
                break

    
    if not status:
        if "rejected" in content:
            status = "rejected"
        elif "approved" in content:
            status = "approved"
        elif "manual_review" in content or "manual review" in content:
            status = "manual_review"
        else:
            status = "needs_more_info"


    if retries >= 2 and status == "needs_more_info":
        status = "manual_review"

    print(f" Auditor Verdict: {status.upper()}")

    return {
        "resolution_status": status,
        "history": [f"Auditor (Attempt {retries}): Verdict = '{status}'. Reasoning: {response.content[:200]}"]
    }