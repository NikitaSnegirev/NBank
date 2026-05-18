import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.create_user_request import CreateUserRequest


@pytest.mark.api
class TestUpdateProfile:
    def test_update_name_in_the_profile(self, api_manager: ApiManager, created_user_request: CreateUserRequest):
        profile = api_manager.customer_management_steps.update_profile(created_user_request, name="John Smith")
        assert profile.customer.name == "John Smith"

    @pytest.mark.parametrize(
        argnames='name',
        argvalues=[
            "JohnSmith",
            "John_Smith",
            "John Smith.",
            "",
            "1John Smith",
        ]
    )
    def test_update_profile_bad_name(self, api_manager: ApiManager, created_user_request: CreateUserRequest, name: str):
        api_manager.customer_management_steps.update_profile_bad_name(created_user_request, name=name, error_text="Name must contain two words with letters only")
        assert api_manager.customer_management_steps.get_profile(created_user_request).name is None