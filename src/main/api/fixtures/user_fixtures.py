import pytest

from src.main.api.generators.random_model_generator import RandomModelGenerator
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.classes.api_manager import ApiManager


@pytest.fixture(scope='function')
def user_request(created_user_factory):
    return created_user_factory()

@pytest.fixture
def created_user_factory(api_manager: ApiManager):
    def _create_user():
        user_data = RandomModelGenerator.generate(CreateUserRequest)
        api_manager.admin_steps.create_user(user_data)
        return user_data

    return _create_user


@pytest.fixture
def created_account_factory(api_manager: ApiManager, created_user_factory):
    def _create_account(balance: float = 0):
        user = created_user_factory()
        account = api_manager.user_steps.create_account(user)

        if balance > 0:
            while balance != 0:
                if balance < 5000:
                    account = api_manager.manage_user_accounts_steps.increase_deposit(
                        user,
                        account.id,
                        balance
                    )
                    balance -= balance
                else:
                    account = api_manager.manage_user_accounts_steps.increase_deposit(
                        user,
                        account.id,
                        5000
                    )
                    balance -= 5000

        return user, account

    return _create_account

@pytest.fixture
def admin_user_request():
    return CreateUserRequest(username='admin', password='admin', role='ADMIN')
