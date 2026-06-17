from src.main.api.models.base_model import BaseModel

class DepositRequest(BaseModel):
    accountId: int
    amount: float