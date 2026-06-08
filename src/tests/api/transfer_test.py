import pytest

from src.main.api.assertions.transaction_assertions import TransactionAssertions
from src.main.api.classes.api_manager import ApiManager
from src.main.api.generators.random_data import RandomData
from src.main.api.generators.random_model_generator import RandomModelGenerator
from src.main.api.models.transaction_type import TransactionType
from src.main.api.models.transfer_request import TransferRequest
from src.main.api.specs.response_specs import ResponseError


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
        transfer_request = RandomModelGenerator.generate(
            TransferRequest,
            senderAccountId=sender_account.id,
            receiverAccountId=receiver_account.id,
            amount=amount,
        )
        api_manager.manage_user_accounts_steps.transfer(sender, transfer_request)

        account_transactions_sender = api_manager.manage_user_accounts_steps.get_transactions(sender, sender_account.id)
        account_transactions_receiver = api_manager.manage_user_accounts_steps.get_transactions(receiver, receiver_account.id)

        TransactionAssertions.has_transaction_with_amount(
            account_transactions_sender,
            TransactionType.TRANSFER_OUT,
            amount
        )

        TransactionAssertions.has_transaction_with_amount(
            account_transactions_receiver,
            TransactionType.TRANSFER_IN,
            amount
        )

    def test_transfer_between_one_users(self, api_manager: ApiManager, created_account_factory, amount=RandomData.get_random_number_float(1, 1000000)):
        sender, account_1 = created_account_factory(balance=10000)
        account_2 = api_manager.user_steps.create_account(sender)

        transfer_request = RandomModelGenerator.generate(
            TransferRequest,
            senderAccountId=account_1.id,
            receiverAccountId=account_2.id,
            amount=amount,
        )

        api_manager.manage_user_accounts_steps.transfer(sender, transfer_request)

        account_transactions_1 = api_manager.manage_user_accounts_steps.get_transactions(sender, account_1.id)
        account_transactions_2 = api_manager.manage_user_accounts_steps.get_transactions(sender, account_2.id)

        TransactionAssertions.has_transaction_with_amount(
            account_transactions_1,
            TransactionType.TRANSFER_OUT,
            amount
        )

        TransactionAssertions.has_transaction_with_amount(
            account_transactions_2,
            TransactionType.TRANSFER_IN,
            amount
        )

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

        transfer_request = RandomModelGenerator.generate(
            TransferRequest,
            senderAccountId=sender_account.id,
            receiverAccountId=receiver_account.id,
            amount=amount,
        )

        api_manager.manage_user_accounts_steps.transfer_bad_request(sender, transfer_request, ResponseError.MAX_TRANSFER_AMOUNT)

        account_transactions_sender = api_manager.manage_user_accounts_steps.get_transactions(sender, sender_account.id)

        TransactionAssertions.has_no_transaction_by_type(
            account_transactions_sender,
            TransactionType.TRANSFER_OUT
        )


    def test_transfer_below_minimum(self, api_manager: ApiManager, created_account_factory):
        sender, sender_account = created_account_factory(balance=3000)
        receiver, receiver_account = created_account_factory()

        transfer_request = RandomModelGenerator.generate(
            TransferRequest,
            senderAccountId=sender_account.id,
            receiverAccountId=receiver_account.id,
            amount=-1,
        )

        api_manager.manage_user_accounts_steps.transfer_bad_request(sender, transfer_request, ResponseError.MIN_TRANSFER_AMOUNT)

        account_transactions_sender = api_manager.manage_user_accounts_steps.get_transactions(sender, sender_account.id)

        TransactionAssertions.has_no_transaction_by_type(
            account_transactions_sender,
            TransactionType.TRANSFER_OUT
        )

    def test_transfer_below_balance(self, api_manager: ApiManager, created_account_factory):
        sender, sender_account = created_account_factory(balance=3000)
        receiver, receiver_account = created_account_factory()

        transfer_request = RandomModelGenerator.generate(
            TransferRequest,
            senderAccountId=sender_account.id,
            receiverAccountId=receiver_account.id,
            amount=3000.01,
        )

        api_manager.manage_user_accounts_steps.transfer_bad_request(sender, transfer_request, ResponseError.INVALID_TRANSFER)

        account_transactions_sender = api_manager.manage_user_accounts_steps.get_transactions(sender, sender_account.id)

        TransactionAssertions.has_no_transaction_by_type(
            account_transactions_sender,
            TransactionType.TRANSFER_OUT
        )
