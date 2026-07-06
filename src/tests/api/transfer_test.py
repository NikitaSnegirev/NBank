from decimal import Decimal

import pytest

from src.main.api.assertions.db_assertions import DbAssertions
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

        account_transactions_sender = api_manager.database_steps.get_transactions_by_account_id(sender_account.id)
        account_transactions_receiver = api_manager.database_steps.get_transactions_by_account_id(receiver_account.id)

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

        transfer_out_transaction = TransactionAssertions.get_transaction_by_type(
            account_transactions_sender,
            TransactionType.TRANSFER_OUT
        )

        transfer_in_transaction = TransactionAssertions.get_transaction_by_type(
            account_transactions_receiver,
            TransactionType.TRANSFER_IN
        )

        sender_account_dao = api_manager.database_steps.get_account_by_account_number(sender_account.accountNumber)
        receiver_account_dao = api_manager.database_steps.get_account_by_account_number(receiver_account.accountNumber)

        assert sender_account_dao.balance == Decimal(str(sender_account.balance)) - Decimal(str(amount))
        assert receiver_account_dao.balance == Decimal(str(receiver_account.balance)) + Decimal(str(amount))

        assert transfer_out_transaction.account_id == sender_account.id
        assert transfer_out_transaction.related_account_id == receiver_account.id
        assert transfer_in_transaction.account_id == receiver_account.id
        assert transfer_in_transaction.related_account_id == sender_account.id

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

        account_transactions_1 = api_manager.database_steps.get_transactions_by_account_id(account_1.id)
        account_transactions_2 = api_manager.database_steps.get_transactions_by_account_id(account_2.id)

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

        transfer_out_transaction = TransactionAssertions.get_transaction_by_type(
            account_transactions_1,
            TransactionType.TRANSFER_OUT
        )

        transfer_in_transaction = TransactionAssertions.get_transaction_by_type(
            account_transactions_2,
            TransactionType.TRANSFER_IN
        )

        sender_account_dao = api_manager.database_steps.get_account_by_account_number(account_1.accountNumber)
        receiver_account_dao = api_manager.database_steps.get_account_by_account_number(account_2.accountNumber)

        assert sender_account_dao.balance == Decimal(str(account_1.balance)) - Decimal(str(amount))
        assert receiver_account_dao.balance == Decimal(str(account_2.balance)) + Decimal(str(amount))

        assert transfer_out_transaction.account_id == account_1.id
        assert transfer_out_transaction.related_account_id == account_2.id
        assert transfer_in_transaction.account_id == account_2.id
        assert transfer_in_transaction.related_account_id == account_1.id

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

        account_transactions_sender = api_manager.database_steps.get_transactions_by_account_id(sender_account.id)

        TransactionAssertions.has_no_transaction_by_type(
            account_transactions_sender,
            TransactionType.TRANSFER_OUT
        )

        sender_account_dao = api_manager.database_steps.get_account_by_account_number(sender_account.accountNumber)
        receiver_account_dao = api_manager.database_steps.get_account_by_account_number(receiver_account.accountNumber)

        assert sender_account_dao.balance == Decimal(str(sender_account.balance))
        assert receiver_account_dao.balance == Decimal(str(receiver_account.balance))

        DbAssertions.has_no_transactions_by_related_account_id(api_manager, receiver_account.id)


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

        account_transactions_sender = api_manager.database_steps.get_transactions_by_account_id(sender_account.id)

        TransactionAssertions.has_no_transaction_by_type(
            account_transactions_sender,
            TransactionType.TRANSFER_OUT
        )

        sender_account_dao = api_manager.database_steps.get_account_by_account_number(sender_account.accountNumber)
        receiver_account_dao = api_manager.database_steps.get_account_by_account_number(receiver_account.accountNumber)

        assert sender_account_dao.balance == Decimal(str(sender_account.balance))
        assert receiver_account_dao.balance == Decimal(str(receiver_account.balance))

        DbAssertions.has_no_transactions_by_related_account_id(api_manager, receiver_account.id)

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

        account_transactions_sender = api_manager.database_steps.get_transactions_by_account_id(sender_account.id)

        TransactionAssertions.has_no_transaction_by_type(
            account_transactions_sender,
            TransactionType.TRANSFER_OUT
        )

        sender_account_dao = api_manager.database_steps.get_account_by_account_number(sender_account.accountNumber)
        receiver_account_dao = api_manager.database_steps.get_account_by_account_number(receiver_account.accountNumber)

        assert sender_account_dao.balance == Decimal(str(sender_account.balance))
        assert receiver_account_dao.balance == Decimal(str(receiver_account.balance))

        DbAssertions.has_no_transactions_by_related_account_id(api_manager, receiver_account.id)
