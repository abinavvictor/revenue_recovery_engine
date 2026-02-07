from pydantic import BaseModel, Field
from typing import List, Optional

class EvidencePack(BaseModel):
    """The structured output for a bank dispute submission."""
    is_contradiction: bool = Field(description="Whether the user claim contradicts logistics data.")
    confidence_score: float = Field(description="A score from 0 to 1 on how certain the AI is of fraud.")
    summary_of_findings: str = Field(description="A concise technical summary of the contradiction.")
    carrier_data_reference: str = Field(description="The specific tracking event used as evidence.")
    recommended_action: str = Field(description="Action for the bank: e.g., 'REJECT_DISPUTE' or 'APPROVE_REFUND'.")

class DisputeAuditResponse(BaseModel):
    """The wrapper for the auditor's internal reasoning."""
    reasoning_steps: List[str]
    final_verdict: EvidencePack