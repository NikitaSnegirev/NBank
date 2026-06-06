import pytest

from src.main.api.classes.session_storage import SessionStorage
from src.main.api.configs.config import Config
from src.main.api.generators.random_model_generator import RandomModelGenerator
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.update_profile_request import UpdateProfileRequest


def _generate_user_request() -> CreateUserRequest:
    return RandomModelGenerator.generate(CreateUserRequest)


@pytest.fixture(scope="function")
def new_user_request() -> CreateUserRequest:
    return _generate_user_request()


@pytest.fixture(scope="function")
def create_user_request(new_user_request: CreateUserRequest) -> CreateUserRequest:
    return new_user_request


@pytest.fixture(scope="function")
def user_factory(api_manager: ApiManager):
    def create_user() -> CreateUserRequest:
        user_data = _generate_user_request()
        api_manager.admin_steps.create_user(user_data)
        return user_data

    yield create_user


@pytest.fixture(scope='function')
def user_request(user_factory):
    try:
        return SessionStorage.get_user(0)
    except Exception:
        user = user_factory()
        return user

@pytest.fixture(scope="function")
def update_profile_request() -> UpdateProfileRequest:
    return RandomModelGenerator.generate(UpdateProfileRequest)

@pytest.fixture
def created_account_factory(api_manager: ApiManager, user_factory):
    def _create_account(balance: float = 0, user: CreateUserRequest | None = None):
        user = user or user_factory()
        account = api_manager.user_steps.create_account(user)

        if balance > 0:
            while balance != 0:
                if balance < 5000:
                    account = api_manager.manage_user_accounts_steps.deposit(
                        user,
                        account.id,
                        balance
                    )
                    balance -= balance
                else:
                    account = api_manager.manage_user_accounts_steps.deposit(
                        user,
                        account.id,
                        5000
                    )
                    balance -= 5000

        return user, account

    return _create_account

@pytest.fixture
def admin_user_request():
    return CreateUserRequest(username=Config.get('ADMIN_USERNAME'), password=Config.get('ADMIN_PASSWORD'), role=Config.get('ADMIN_ROLE'))
