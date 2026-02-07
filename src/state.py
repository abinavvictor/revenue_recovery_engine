import operator
from typing import Annotated, List, Literal
from typing_extensions import TypedDict


class DisputeState(TypedDict):
    # 'operator.add' allows us to append to the history as we move through nodes
    history: Annotated[List[str], operator.add]
    order_id: str
    user_claim: str
    shipping_status: str
    is_contradiction: bool
    resolution_status: Literal["pending", "win_recommended", "loss_predicted", "manual_review"]
    retry_count: int