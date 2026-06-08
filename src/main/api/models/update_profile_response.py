from src.main.api.models.base_model import BaseModel
from src.main.api.models.get_profile_response import GetProfileResponse


class UpdateProfileResponse(BaseModel):
    message: str
    customer: GetProfileResponse