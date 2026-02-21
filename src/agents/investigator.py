import ast
import os
import httpx
from langchain_groq import ChatGroq
from src.state import DisputeState

async def investigator_node(state: DisputeState):
    order_id = state['order_id']
    retries = state.get("retry_count", 0)
    session = state["mcp_session"]

    print(f"Investigator (Attempt {retries + 1}) ---")

    #For personal ref:MCP wraps results in CallToolResult(content=[TextContent(text="...")]).so retrieving actual string as result.content[0].text
    try:
        db_result = await session.call_tool(
            "access_database",
            arguments={"sql_command": f"SELECT order_id, customer_name, status, tracking_num, stripe_pi_id FROM orders WHERE order_id = '{order_id}';"}
        )
        if hasattr(db_result, 'content') and isinstance(db_result.content, list):
            db_raw = db_result.content[0].text
        else:
            db_raw = str(db_result)
        print(f"DB Parsed: {db_raw}")
    except Exception as e:
        db_raw = f"DB Error: {str(e)}"
        print(f" DB Exception: {e}")

    
    tracking_num = None
    try:
        records = ast.literal_eval(db_raw)
        if records:
            tracking_num = records[0].get("tracking_num")
    except Exception:
        pass

    
    if tracking_num:
        carrier = "shippo" if tracking_num.upper().startswith("SHIPPO_") else \
                  "ups"    if tracking_num.upper().startswith("1Z") else \
                  "fedex"  if tracking_num.upper().startswith("FEDEX") else \
                  "usps"   if len(tracking_num) == 22 else "ups"
        shippo_raw = await _get_tracking_status(tracking_num, carrier)
    else:
        shippo_raw = "Tracking Error: No tracking number found in DB"

    print(f" Shippo: {shippo_raw}")

    # 4. Normalize
    normalized_report = await _normalize_data(db_raw, shippo_raw, order_id)
    print(f" Investigator Report:\n{normalized_report}\n")

    return {
        "shipping_status": normalized_report,
        "history": [f"[Investigation Attempt {retries + 1} for {order_id}]:\n{normalized_report}"],
        "messages": [{"role": "assistant", "content": normalized_report}],
        "retry_count": retries + 1,
    }


async def _get_tracking_status(tracking_num: str, carrier: str = "ups") -> str:
    """Direct carrier tracking via Shippo."""
    api_key = os.getenv("SHIPPO_API_KEY")
    if not api_key:
        return "Tracking Error: SHIPPO_API_KEY not set"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.goshippo.com/tracks/{carrier}/{tracking_num}",
                headers={"Authorization": f"ShippoToken {api_key}"},
                timeout=10.0
            )
            data = response.json()
            status = data.get("tracking_status", {}).get("status", "UNKNOWN")
            location = data.get("tracking_status", {}).get("location") or {}
            city = location.get("city", "")
            return f"Carrier Status: {status}, Last Location: {city}"
    except Exception as e:
        return f"Tracking Error: {str(e)}"


async def _normalize_data(db_data: str, shippo_data: str, order_id: str) -> str:
    model = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

    prompt = f"""
    This engine at core is shipping fraud investigator analyzing a chargeback claim for Order {order_id}.
    A customer claims they DID NOT receive their package.

    DATABASE RECORD (internal order system): {db_data}
    SHIPPO CARRIER DATA (live tracking): {shippo_data}

    DECISION FRAMEWORK — use BOTH sources together:

    DATABASE tells : what the merchant's system recorded (Shipped/Lost/Delivered etc.)
    SHIPPO tells :   what the carrier actually reported in real-time

    CONFLICT RESOLUTION RULES:
    - If DB says Delivered AND Shippo says DELIVERED → Strong fraud signal
    - If DB says Shipped AND Shippo says DELIVERED → Fraud — carrier confirms delivery
    - If DB says Shipped AND Shippo says TRANSIT → Legitimate — package still moving
    - If DB says Lost AND Shippo says FAILURE/RETURNED → Confirmed non-delivery → refund
    - If DB says Lost AND Shippo says DELIVERED → Investigate further — data conflict
    - If Shippo returns UNKNOWN/error → Fall back to DB status as sole source

    Produce this EXACT report — no extra text:

    - ORDER_STATUS: (DB status verbatim)
    - SHIPPO_STATUS: (DELIVERED/TRANSIT/RETURNED/FAILURE/UNKNOWN)
    - TRACKING_NUMBER: (from DB)
    - CARRIER: (detected carrier)
    - LAST_LOCATION: (from Shippo or N/A)
    - STRIPE_PI_ID: (from DB or MISSING)
    - FRAUD_INDICATOR: (YES / NO / INCONCLUSIVE)
    - RECOMMENDATION: (REJECT_CLAIM / APPROVE_REFUND / NEEDS_INVESTIGATION / MONITOR)
    - SUMMARY: (2 sentences — cite BOTH DB and Shippo evidence in your reasoning)
    """

    res = await model.ainvoke(prompt)
    return res.content