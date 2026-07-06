import pytest

from src.main.api.assertions.db_assertions import DbAssertions
from src.main.api.classes.api_manager import ApiManager
from src.main.api.generators.random_data import RandomData
from src.main.api.models.comparison.dao_and_model_assertions import DaoAndModelAssertions
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.transaction_type import TransactionType
from src.main.api.specs.response_specs import ResponseError


@pytest.mark.api
class TestDeposit:
    @pytest.mark.check_transactions_change(account_source="user_account", delta=1)
    @pytest.mark.parametrize(
        argnames='balance',
        argvalues=[
            4999.99,
            0.01,
            RandomData.get_random_number_float(1, 500000)
        ]
    )
    @pytest.mark.usefixtures("user_request", 'api_manager', 'user_account')
    def test_deposit(self, api_manager: ApiManager, user_request: CreateUserRequest, balance: float, user_account):
        deposit = api_manager.manage_user_accounts_steps.deposit(user_request, user_account.id, balance)
        account_transactions = api_manager.manage_user_accounts_steps.get_transactions(user_request, user_account.id)
        transaction = account_transactions[0]

        assert deposit.balance == balance
        assert deposit.transactionId == transaction.id
        assert transaction.amount == balance
        assert transaction.type == TransactionType.DEPOSIT
        assert transaction.relatedAccountId == user_account.id

        assert account_transactions[0].amount == transaction.amount

        account_dao = api_manager.database_steps.find_account_by_account_number(deposit.accountNumber)
        DaoAndModelAssertions.assert_that(deposit, account_dao).match()

        transactions_dao = api_manager.database_steps.get_transactions_by_transaction_id(transaction.id)
        DaoAndModelAssertions.assert_that(transaction, transactions_dao).match()

    @pytest.mark.check_transactions_change(account_source="user_account", delta=0)
    @pytest.mark.parametrize(
        argnames='balance, error_text',
        argvalues=[
            (5000.1, ResponseError.DEPOSIT_OVER_LIMIT),
            (5001, ResponseError.DEPOSIT_OVER_LIMIT),
            (0, ResponseError.MIN_DEPOSIT_AMOUNT),
            (-1, ResponseError.MIN_DEPOSIT_AMOUNT),
        ]
    )
    @pytest.mark.usefixtures("user_request", 'api_manager', 'user_account')
    def test_deposit_incorrect_balance(self, api_manager: ApiManager, user_request: CreateUserRequest, balance: float, error_text: ResponseError, user_account):
        api_manager.manage_user_accounts_steps.deposit_bad_request(user_request, user_account.id, balance, error_text)

        account_dao = api_manager.database_steps.get_account_by_account_number(user_account.accountNumber)
        DaoAndModelAssertions.assert_that(user_account, account_dao).match()

        DbAssertions.has_no_transactions_by_related_account_id(api_manager, user_account.id)

    @pytest.mark.check_transactions_change(account_source="user_account", delta=0)
    @pytest.mark.usefixtures("user_request", 'api_manager')
    def test_deposit_another_user_id(self, api_manager: ApiManager, user_factory, user_request: CreateUserRequest):
        user_1 = user_factory()
        user_2 = user_factory()

        user_1_account = api_manager.user_steps.create_account(user_1)
        user_2_account = api_manager.user_steps.create_account(user_2)

        api_manager.manage_user_accounts_steps.deposit_bad_request(user_1, user_2_account.id, 100, ResponseError.UNAUTHORIZED_ACCESS_TO_ACCOUNT)

        account_dao_1 = api_manager.database_steps.get_account_by_account_number(user_1_account.accountNumber)
        DaoAndModelAssertions.assert_that(user_1_account, account_dao_1).match()

        account_dao_2 = api_manager.database_steps.get_account_by_account_number(user_2_account.accountNumber)
        DaoAndModelAssertions.assert_that(user_2_account, account_dao_2).match()

        DbAssertions.has_no_transactions_by_related_account_id(api_manager, user_1_account.id)

    @pytest.mark.check_transactions_change(account_source="user_account", delta=0)
    @pytest.mark.usefixtures("user_request", 'api_manager', 'user_account')
    def test_deposit_non_exist_id(self, api_manager: ApiManager, user_factory, user_request: CreateUserRequest, user_account):
        api_manager.manage_user_accounts_steps.deposit_bad_request(user_request, 0, 100, ResponseError.UNAUTHORIZED_ACCESS_TO_ACCOUNT)

        account_dao = api_manager.database_steps.get_account_by_account_number(user_account.accountNumber)
        DaoAndModelAssertions.assert_that(user_account, account_dao).match()

        DbAssertions.has_no_transactions_by_related_account_id(api_manager, user_account.id)
