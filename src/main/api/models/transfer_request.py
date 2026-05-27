from typing import Annotated

from src.main.api.generators.generating_rule import GeneratingRule
from src.main.api.models.base_model import BaseModel

class TransferRequest(BaseModel):
    senderAccountId: int
    receiverAccountId: int
    amount: Annotated[float, GeneratingRule(regex=r"^[1-9][0-9]{0,3}(\.[0-9]{1,2})?$")]
