import pytest
from playwright.sync_api import Page, expect

from src.main.api.assertions.transaction_assertions import TransactionAssertions
from src.main.api.classes.api_manager import ApiManager
from src.main.api.generators.random_data import RandomData
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.ui.pages.bank_alert import BankAlert, successfully_deposited
from src.main.ui.pages.deposit_money import DepositMoney
from src.main.ui.pages.user_dashboard import UserDashboard


@pytest.mark.ui
class TestDeposit:
    @pytest.mark.user_session(1)
    @pytest.mark.check_transactions_change(account_source="user_account", delta=1)
    def test_user_can_deposit(
            self,
            api_manager: ApiManager,
            page: Page,
            user_request: CreateUserRequest,
            user_account,
            amount: str = str(RandomData.get_random_number_float(1, 500000)),
    ):
        UserDashboard(page).open() \
        .check_page_is_visible() \
        .deposit_money() \
        .check_page_is_visible() \
        .select_account(str(user_account.id)) \
        .enter_amount(amount) \
        .deposit_click_and_check_msg(
            successfully_deposited(amount, user_account.accountNumber)
        )

        transactions = api_manager.database_steps.get_transactions_by_account_id(user_account.id)
        assert str(transactions[0].amount) == amount

    @pytest.mark.parametrize(
        argnames='amount, error_text',
        argvalues=[
            ("5000.1", BankAlert.AMOUNT_MORE_THAN_5000_DEPOSIT),
            ("-1", BankAlert.INVALID_AMOUNT_DEPOSIT),
        ]
    )
    @pytest.mark.user_session(1)
    @pytest.mark.check_transactions_change(account_source="user_account", delta=0)
    def test_deposit_incorrect_balance(
            self,
            api_manager: ApiManager,
            page: Page,
            user_request: CreateUserRequest,
            user_account,
            amount: str,
            error_text: str
    ):
        (DepositMoney(page).open() \
        .check_page_is_visible() \
        .select_account(str(user_account.id))) \
        .enter_amount(amount) \
        .deposit_click_and_check_msg(error_text)

    @pytest.mark.user_session(1)
    @pytest.mark.check_transactions_change(account_source="user_account", delta=0)
    def test_account_not_selected_deposit(
            self,
            api_manager: ApiManager,
            page: Page,
            user_request: CreateUserRequest,
            user_account,
            amount: str = str(RandomData.get_random_number_float(1, 500000))
    ):
        DepositMoney(page).open() \
        .check_page_is_visible() \
        .enter_amount(amount) \
        .deposit_click_and_check_msg(BankAlert.ACCOUNT_NOT_SELECTED_DEPOSIT)