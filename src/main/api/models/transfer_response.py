from typing import Optional

from src.main.api.models.base_model import BaseModel


class TransferResponse(BaseModel):
    status: str
    message: str

    amount: float
    senderAccountId: int
    receiverAccountId: int

    fraudRiskScore: Optional[float] = None
    fraudReason: Optional[str] = None
    requiresManualReview: Optional[bool] = None
    requiresVerification: Optional[bool] = None