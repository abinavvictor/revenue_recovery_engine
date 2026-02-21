import ast
from langchain_groq import ChatGroq
from src.state import DisputeState

async def refund_node(state: DisputeState):
    order_id = state['order_id']
    session = state["mcp_session"]
    print(f" [NODE]: Refund Initiator for {order_id}")

    stripe_pi_id = None
    try:
        pi_result = await session.call_tool(
            "access_database",
            arguments={"sql_command": f"SELECT stripe_pi_id, customer_name FROM orders WHERE order_id = '{order_id}';"}
        )
        
        if hasattr(pi_result, 'content') and isinstance(pi_result.content, list):
            pi_raw = pi_result.content[0].text
        else:
            pi_raw = str(pi_result)

        print(f" Raw PI lookup: {pi_raw}")
        records = ast.literal_eval(pi_raw)
        if records:
            stripe_pi_id = records[0].get("stripe_pi_id")
        print(f" Stripe PI ID: {stripe_pi_id}")
    except Exception as e:
        print(f" Could not fetch stripe_pi_id: {e}")

    if not stripe_pi_id:
        print(" No stripe_pi_id found — escalating to manual review.")
        return {
            "history": [f"Refund FAILED for {order_id}: stripe_pi_id missing in DB."],
            "resolution_status": "manual_review"
        }

    tools = state["mcp_tools"]
    model = ChatGroq(model="llama-3.3-70b-versatile").bind_tools(tools)

    prompt = f"""
    The auditor has confirmed non-delivery for Order {order_id}. Process the refund now.
    Stripe Payment Intent ID: {stripe_pi_id}
    Steps:
    1. Call get_payment_details with payment_intent_id="{stripe_pi_id}" to confirm it is in 'succeeded' state.
    2. If confirmed, call process_refund with payment_intent_id="{stripe_pi_id}" and amount_cents=0 for a full refund.
    3. Confirm completion.
    """

    response = await model.ainvoke(prompt)
    if response.content:
        refund_summary = response.content if isinstance(response.content, str) else str(response.content)
    else:
        refund_summary = f"Refund tool called for PI {stripe_pi_id}"
        
    print(f" Refund Response: {refund_summary[:200]}")

    try:
        await session.call_tool(
            "access_database",
            arguments={"sql_command": f"INSERT INTO audit_logs (order_id, action, detail, created_at) VALUES ('{order_id}', 'REFUND_INITIATED', 'stripe_pi_id: {stripe_pi_id}', NOW());"}
        )
    except Exception as e:
        print(f" Audit log write failed: {e}")

    return {
        "history": [f"Refund executed for {order_id} via PI {stripe_pi_id}."],
        "messages": [response],
        "resolution_status": "refund_completed"
    }