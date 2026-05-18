from src.main.api.models.base_model import BaseModel
from src.main.api.models.create_account_response import CreateAccountResponse


class GetProfileResponse(BaseModel):
    id: int
    username: str
    password: str
    name: str
    role: str
    accounts: list[CreateAccountResponse]