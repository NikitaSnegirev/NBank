import pytest

from src.main.api.classes.api_manager import ApiManager

@pytest.mark.api
class TestTransfer:

    @pytest.mark.parametrize(
        argnames='amount',
        argvalues=[
            9999.99,
            0.01,
        ]
    )
    def test_transfer_between_users(self, api_manager: ApiManager, created_account_factory, amount: float):
        sender, sender_account = created_account_factory(balance=10000)
        receiver, receiver_account = created_account_factory()

        api_manager.manage_user_accounts_steps.transfer(sender, sender_account.id, receiver_account.id, amount)

    def test_transfer_between_one_users(self, api_manager: ApiManager, created_account_factory):
        sender, account_1 = created_account_factory(balance=3000)
        account_2 = api_manager.user_steps.create_account(sender)

        api_manager.manage_user_accounts_steps.transfer(sender, account_1.id, account_2.id, 1000)

    @pytest.mark.parametrize(
        argnames='amount',
        argvalues=[
            10000.01,
            10001,
        ]
    )
    def test_transfer_over_limit(self, api_manager: ApiManager, created_account_factory, amount: float):
        sender, sender_account = created_account_factory(balance=10000.01)
        receiver, receiver_account = created_account_factory()

        api_manager.manage_user_accounts_steps.transfer_bad_request(sender, sender_account.id, receiver_account.id, amount, "Transfer amount cannot exceed 10000")

    def test_transfer_below_minimum(self, api_manager: ApiManager, created_account_factory):
        sender, sender_account = created_account_factory(balance=3000)
        receiver, receiver_account = created_account_factory()

        api_manager.manage_user_accounts_steps.transfer_bad_request(sender, sender_account.id, receiver_account.id, -1, "Transfer amount must be at least 0.01")

    def test_transfer_below_balance(self, api_manager: ApiManager, created_account_factory):
        sender, sender_account = created_account_factory(balance=3000)
        receiver, receiver_account = created_account_factory()

        api_manager.manage_user_accounts_steps.transfer_bad_request(sender, sender_account.id, receiver_account.id, 3000.01, "Invalid transfer: insufficient funds or invalid accounts")

