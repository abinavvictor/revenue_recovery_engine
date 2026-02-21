from typing import Any, List
from typing_extensions import TypedDict

class DisputeState(TypedDict):
    order_id: str
    mcp_session: Any
    stripe_session: Any
    db_session: Any
    mcp_tools: List[Any]
    history: List[str]
    messages: List[Any]
    retry_count: int
    resolution_status: str
    shipping_status: str       