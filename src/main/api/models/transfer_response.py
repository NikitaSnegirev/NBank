from src.main.api.models.base_model import BaseModel

class TransferResponse(BaseModel):
    receiverAccountId: int
    amount: float
    message: str
    senderAccountId: int