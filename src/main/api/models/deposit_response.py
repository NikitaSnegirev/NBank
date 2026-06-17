from pydantic import BaseModel

from src.main.api.models.transaction_type import TransactionType


class TransactionResponse(BaseModel):
    id: int
    amount: float
    type: TransactionType
    timestamp: str
    relatedAccountId: int


class DepositResponse(BaseModel):
    id: int
    accountNumber: str
    balance: float
    depositAmount: float
    transactionId: int