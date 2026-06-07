from src.main.api.models.base_model import BaseModel
from src.main.api.models.create_account_response import CreateAccountResponse
from src.main.api.models.deposit_response import DepositResponse


class AdminUserResponse(BaseModel):
    id: int
    username: str
    name: str | None
    role: str
    accounts: list[CreateAccountResponse]