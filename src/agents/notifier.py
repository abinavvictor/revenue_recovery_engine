import ast
from langchain_groq import ChatGroq
from src.state import DisputeState

async def notifier_node(state: DisputeState):
    status = state.get("resolution_status")
    retries = state.get("retry_count", 0)
    order_id = state.get("order_id")
    session = state["mcp_session"]

    print(f" [NODE]: Notifier — Status: {status}, Attempts: {retries}")

    
    customer_name = "Valued Customer"
    customer_email = "customer@example.com"
    try:
        result = await session.call_tool(
            "access_database",
            arguments={"sql_command": f"SELECT customer_name, customer_email FROM orders WHERE order_id = '{order_id}';"}
        )
        if hasattr(result, 'content') and isinstance(result.content, list):
            raw = result.content[0].text
        else:
            raw = str(result)
        records = ast.literal_eval(raw)
        if records:
            customer_name = records[0].get("customer_name", customer_name)
            customer_email = records[0].get("customer_email", customer_email)
    except Exception:
        pass

    
    templates = {
        "rejected": {
            "label": " CHARGEBACK DEFENDED",
            "subject": f"Update on Your Dispute — Order #{order_id}",
            "body": f"""Dear {customer_name},

We have completed our investigation of your dispute for Order #{order_id}.

Our records, including carrier tracking data, confirm that your order was successfully delivered. As a result, we are unable to process a refund for this order and will be providing this evidence to defend the chargeback.

If you believe this is an error, please contact our support team with any additional documentation.

Thank you for your understanding."""
        },
        "approved": {
            "label": "REFUND APPROVED",
            "subject": f"Refund Confirmed — Order #{order_id}",
            "body": f"""Dear {customer_name},

We have completed our investigation of your dispute for Order #{order_id}.

Our records confirm that your shipment did not reach you as expected. We sincerely apologize for this experience. A full refund has been processed and will appear in your account within 3–5 business days.

Thank you for your patience."""
        },
        "refund_completed": {
            "label": "REFUND PROCESSED",
            "subject": f"Refund Processed — Order #{order_id}",
            "body": f"""Dear {customer_name},

Your refund for Order #{order_id} has been successfully processed via Stripe. Please allow 3–5 business days for it to reflect in your account.

We apologize for the inconvenience and appreciate your patience."""
        },
        "manual_review": {
            "label": " ESCALATED TO SPECIALIST",
            "subject": f"Your Case is Under Review — Order #{order_id}",
            "body": f"""Dear {customer_name},

Thank you for your patience. Your dispute for Order #{order_id} requires additional review by our specialist team.

A member of our team will contact you within 24–48 hours with a resolution. We appreciate your understanding."""
        },
    }

    config = templates.get(status, {
        "label": " STATUS UPDATE",
        "subject": f"Update on Order #{order_id}",
        "body": f"Dear {customer_name}, the status of your case for Order #{order_id} is: {status}."
    })

    
    tools = state["mcp_tools"]
    model = ChatGroq(model="llama-3.3-70b-versatile").bind_tools(tools)

    prompt = f"""
    Send a customer notification email using the send_email tool.
    to: "{customer_email}"
    subject: "{config['subject']}"
    body: "{config['body']}"
    Call send_email now with these exact values.
    """

    await model.ainvoke(prompt)
    print(f"{config['label']} — Notified: {customer_email}")

    #This is best part, writing back to build dispute history,in case of future fradulence
    try:
        await session.call_tool(
            "access_database",
            arguments={"sql_command": f"""
                INSERT INTO dispute_history (order_id, resolution, resolved_at)
                VALUES ('{order_id}', '{status}', NOW());
            """}
        )
    except Exception as e:
        print(f" Dispute history log failed: {e}")

    return {
        "history": [f"{config['label']}: Notification sent for {order_id}."],
        "resolution_status": status
    }