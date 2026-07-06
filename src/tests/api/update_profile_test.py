import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.generators.random_model_generator import RandomModelGenerator
from src.main.api.models.comparison.dao_and_model_assertions import DaoAndModelAssertions
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.update_profile_request import UpdateProfileRequest
from src.main.api.specs.response_specs import ResponseError


@pytest.mark.api
class TestUpdateProfile:
    def test_update_name_in_the_profile(self, api_manager: ApiManager, user_request: CreateUserRequest, update_profile_request: UpdateProfileRequest):
        profile = api_manager.customer_management_steps.update_profile(user_request, name=update_profile_request.name)

        assert profile.customer.name == update_profile_request.name

    @pytest.mark.check_name_change(new_name=None)
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
    def test_update_profile_bad_name(self, api_manager: ApiManager, user_request: CreateUserRequest, name: str):
        api_manager.customer_management_steps.update_profile_bad_name(user_request, name=name, error_text=ResponseError.NAME)
        profile = api_manager.customer_management_steps.get_profile(user_request)
        assert profile.name is None

        print(profile)
        customer_dao = api_manager.database_steps.get_customer_by_customer_id(profile.id)
        DaoAndModelAssertions.assert_that(profile, customer_dao).match()
