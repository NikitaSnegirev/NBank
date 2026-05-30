import pytest
from playwright.sync_api import Page, expect

from src.main.api.classes.api_manager import ApiManager
from src.main.api.generators.random_data import RandomData
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.ui.pages.bank_alert import BankAlert, successfully_deposited
from src.main.ui.pages.deposit_money import DepositMoney
from src.main.ui.pages.user_dashboard import UserDashboard


@pytest.mark.ui
class TestIncreaseDeposit:
    @pytest.mark.user_session(1)
    def test_user_can_increase_deposit(
            self,
            api_manager: ApiManager,
            page: Page,
            user_request: CreateUserRequest,
            amount: str = str(RandomData.get_random_number_float(1, 500000))
    ):
        account = api_manager.user_steps.create_account(user_request)

        dashboard_page = UserDashboard(page).open()
        expect(dashboard_page.welcome_text).to_be_visible()

        deposit_page = dashboard_page.deposit_money()
        expect(deposit_page.deposit_money_header).to_be_visible()
        deposit_page.select_account(str(account.id))
        deposit_page.enter_amount(amount)
        deposit_page.deposit_click_and_check_msg(
            successfully_deposited(amount, account.accountNumber)
        )

        transactions = api_manager.manage_user_accounts_steps.get_transactions(user_request,account.id)
        assert str(transactions[0].amount) == amount

    @pytest.mark.parametrize(
        argnames='amount, error_text',
        argvalues=[
            ("5000.1", BankAlert.AMOUNT_MORE_THAN_5000_DEPOSIT),
            ("-1", BankAlert.INVALID_AMOUNT_DEPOSIT),
        ]
    )
    @pytest.mark.user_session(1)
    def test_increase_deposit_incorrect_balance(
            self,
            api_manager: ApiManager,
            page: Page,
            user_request: CreateUserRequest,
            amount: str,
            error_text: str
    ):
        account = api_manager.user_steps.create_account(user_request)

        dashboard_page = UserDashboard(page).open()
        expect(dashboard_page.welcome_text).to_be_visible()

        deposit_page = dashboard_page.deposit_money()
        expect(deposit_page.deposit_money_header).to_be_visible()
        deposit_page.select_account(str(account.id))
        deposit_page.enter_amount(amount)
        deposit_page.deposit_click_and_check_msg(error_text)

    @pytest.mark.user_session(1)
    def test_user_can_increase_deposit(
            self,
            api_manager: ApiManager,
            page: Page,
            user_request: CreateUserRequest,
            amount: str = str(RandomData.get_random_number_float(1, 500000))
    ):
        dashboard_page = UserDashboard(page).open()
        expect(dashboard_page.welcome_text).to_be_visible()

        deposit_page = dashboard_page.deposit_money()
        expect(deposit_page.deposit_money_header).to_be_visible()
        deposit_page.enter_amount(amount)
        deposit_page.deposit_click_and_check_msg(BankAlert.ACCOUNT_NOT_SELECTED_DEPOSIT)