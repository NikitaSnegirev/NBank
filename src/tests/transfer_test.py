import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.generators.random_data import RandomData


@pytest.mark.api
class TestTransfer:

    @pytest.mark.parametrize(
        argnames='amount',
        argvalues=[
            9999.99,
            0.01,
            RandomData.get_random_number_float(1, 1000000)
        ]
    )
    def test_transfer_between_users(self, api_manager: ApiManager, created_account_factory, amount: float):
        sender, sender_account = created_account_factory(balance=10000)
        receiver, receiver_account = created_account_factory()

        api_manager.manage_user_accounts_steps.transfer(sender, sender_account.id, receiver_account.id, amount)

        account_transactions_sender = api_manager.manage_user_accounts_steps.get_transactions(sender, sender_account.id)
        account_transactions_receiver = api_manager.manage_user_accounts_steps.get_transactions(receiver, receiver_account.id)

        assert (self._get_transaction_by_type(account_transactions_sender)).amount == amount
        assert account_transactions_receiver[0].amount == amount

    def test_transfer_between_one_users(self, api_manager: ApiManager, created_account_factory, amount=RandomData.get_random_number_float(1, 500000)):
        sender, account_1 = created_account_factory(balance=5000)
        account_2 = api_manager.user_steps.create_account(sender)

        api_manager.manage_user_accounts_steps.transfer(sender, account_1.id, account_2.id, amount)

        account_transactions_1 = api_manager.manage_user_accounts_steps.get_transactions(sender, account_1.id)
        account_transactions_2 = api_manager.manage_user_accounts_steps.get_transactions(sender, account_2.id)

        assert (self._get_transaction_by_type(account_transactions_1)).amount == amount
        assert account_transactions_2[0].amount == amount

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

        account_transactions_sender = api_manager.manage_user_accounts_steps.get_transactions(sender, sender_account.id)

        assert not self._get_transaction_by_type(account_transactions_sender)


    def test_transfer_below_minimum(self, api_manager: ApiManager, created_account_factory):
        sender, sender_account = created_account_factory(balance=3000)
        receiver, receiver_account = created_account_factory()

        api_manager.manage_user_accounts_steps.transfer_bad_request(sender, sender_account.id, receiver_account.id, -1, "Transfer amount must be at least 0.01")

        account_transactions_sender = api_manager.manage_user_accounts_steps.get_transactions(sender, sender_account.id)

        assert not self._get_transaction_by_type(account_transactions_sender)

    def test_transfer_below_balance(self, api_manager: ApiManager, created_account_factory):
        sender, sender_account = created_account_factory(balance=3000)
        receiver, receiver_account = created_account_factory()

        api_manager.manage_user_accounts_steps.transfer_bad_request(sender, sender_account.id, receiver_account.id, 3000.01, "Invalid transfer: insufficient funds or invalid accounts")

        account_transactions_sender = api_manager.manage_user_accounts_steps.get_transactions(sender, sender_account.id)

        assert not self._get_transaction_by_type(account_transactions_sender)


    def _get_transaction_by_type(self, transactions: list):
        filtered_transactions = [
            transaction
            for transaction in transactions
            if transaction.type == "TRANSFER_OUT"
        ]

        if len(filtered_transactions) > 0 :
            return filtered_transactions[0]
        else:
            return None