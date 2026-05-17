from pydantic import BaseModel
from typing import List


class TransactionResponse(BaseModel):
    id: int
    amount: float
    type: str
    timestamp: str
    relatedAccountId: int


class IncreaseDepositResponse(BaseModel):
    id: int
    accountNumber: str
    balance: float
    transactions: List[TransactionResponse]