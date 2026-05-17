import pytest

from src.main.api.generators.random_model_generator import RandomModelGenerator
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.classes.api_manager import ApiManager


@pytest.fixture(scope='function')
def created_user_request(created_user_factory):
    return created_user_factory()

@pytest.fixture
def created_user_factory(api_manager: ApiManager):
    def _create_user():
        user_data = RandomModelGenerator.generate(CreateUserRequest)
        api_manager.admin_steps.create_user(user_data)
        return user_data

    return _create_user

@pytest.fixture
def admin_user_request():
    return CreateUserRequest(username='admin', password='admin', role='ADMIN')
