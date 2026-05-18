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
            RandomData.get_random_number_divided_by_one_hundred(1, 500000)
        ]
    )
    @pytest.mark.usefixtures("created_user_request", 'api_manager')
    def test_increase_deposit(self, api_manager: ApiManager, created_user_request: CreateUserRequest, balance: float):
        account = api_manager.user_steps.create_account(created_user_request)
        deposit = api_manager.manage_user_accounts_steps.increase_deposit(created_user_request, account.id, balance)
        transaction = deposit.transactions[0]

        assert deposit.balance == balance
        assert transaction.amount == balance
        assert transaction.type == "DEPOSIT"
        assert transaction.relatedAccountId == account.id

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
    def test_increase_deposit_incorrect_balance(self, api_manager: ApiManager, created_user_request: CreateUserRequest, balance: float, error_text: str):
        account = api_manager.user_steps.create_account(created_user_request)
        api_manager.manage_user_accounts_steps.increase_deposit_bad_request(created_user_request, account.id, balance, error_text)

    @pytest.mark.usefixtures("created_user_request", 'api_manager')
    def test_increase_deposit_another_user_id(self, api_manager: ApiManager, created_user_factory, created_user_request: CreateUserRequest):
        user_1 = created_user_factory()
        user_2 = created_user_factory()

        user_1_account = api_manager.user_steps.create_account(user_1)
        user_2_account = api_manager.user_steps.create_account(user_2)

        api_manager.manage_user_accounts_steps.increase_deposit_bad_request(user_1, user_2_account.id, 100, "Unauthorized access to account")

    @pytest.mark.usefixtures("created_user_request", 'api_manager')
    def test_increase_deposit_non_exist_id(self, api_manager: ApiManager, created_user_factory, created_user_request: CreateUserRequest):
        api_manager.user_steps.create_account(created_user_request)
        api_manager.manage_user_accounts_steps.increase_deposit_bad_request(created_user_request, 0, 100, "Unauthorized access to account")


