import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.create_user_request import CreateUserRequest


@pytest.mark.api
class TestCreateAccount:
    @pytest.mark.usefixtures("created_user_request", 'api_manager')
    def test_create_account(self, api_manager: ApiManager, created_user_request: CreateUserRequest):
        api_manager.user_steps.create_account(created_user_request)