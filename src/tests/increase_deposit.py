import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.generators.random_data import RandomData
from src.main.api.models.create_user_request import CreateUserRequest


@pytest.mark.api
class TestIncreaseDeposit:
    @pytest.mark.parametrize(
        argnames='balance',
        argvalues=[
            4999.99,
            0.01,
        ]
    )
    @pytest.mark.usefixtures("created_user_request", 'api_manager')
    def test_increase_deposit(self, api_manager: ApiManager, created_user_request: CreateUserRequest, balance: int):
        account = api_manager.user_steps.create_account(created_user_request)
        api_manager.user_steps.increase_deposit(created_user_request, account.id, balance)

    @pytest.mark.parametrize(
        argnames='balance, error_text',
        argvalues=[
            (5000.1, 'Deposit amount cannot exceed 5000'),
            (5001, 'Deposit amount cannot exceed 5000'),
            (0, 'Deposit amount must be at least 0.01'),
            (-1, 'Deposit amount must be at least 0.01'),
        ]
    )
    @pytest.mark.usefixtures("created_user_request", 'api_manager')
    def test_increase_deposit_incorrect_balance(self, api_manager: ApiManager, created_user_request: CreateUserRequest,
                                                balance: int, error_text: str):
        account = api_manager.user_steps.create_account(created_user_request)
        api_manager.user_steps.increase_deposit_over_limit(created_user_request, account.id, balance, error_text)
