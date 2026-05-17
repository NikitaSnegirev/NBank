from src.main.api.models.base_model import BaseModel

class IncreaseDepositRequest(BaseModel):
    id: int
    balance: float