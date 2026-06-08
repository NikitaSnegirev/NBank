from datetime import datetime

from pydantic.dataclasses import dataclass


@dataclass
class TransactionsDao:
    id: int
    amount: float
    type: str
    timestamp: datetime
    account_id: int
    related_account_id: int
    created_at: datetime