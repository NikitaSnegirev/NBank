import pytest
from playwright.sync_api import Page, expect

from src.main.api.assertions.transaction_assertions import TransactionAssertions
from src.main.api.classes.api_manager import ApiManager
from src.main.api.classes.session_storage import SessionStorage
from src.main.api.generators.random_data import RandomData
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.transaction_type import TransactionType
from src.main.ui.pages.bank_alert import successfully_transferred, BankAlert
from src.main.ui.pages.make_transfer import MakeTransfer
from src.main.ui.pages.user_dashboard import UserDashboard


@pytest.mark.ui
class TestTransfer:
    @pytest.mark.user_session(2)
    def test_transfer_between_users(
            self,
            api_manager: ApiManager,
            page: Page,
            user_request: CreateUserRequest,
            created_account_factory,
            amount: str = str(RandomData.get_random_number_float(1, 1000000))
    ):
        sender = SessionStorage.get_user(0)
        receiver = SessionStorage.get_user(1)

        sender, sender_account = created_account_factory(user=sender, balance=10000)
        receiver, receiver_account = created_account_factory(user=receiver)

        UserDashboard(page).open() \
        .check_page_is_visible() \
        .make_transfer() \
        .check_page_is_visible() \
        .select_account(str(sender_account.id)) \
        .recipient_name(receiver.username) \
        .recipient_account_number(str(receiver_account.accountNumber)) \
        .enter_amount(amount) \
        .confirm_check_click() \
        .send_transfer_and_check_msg(
            successfully_transferred(amount, str(receiver_account.accountNumber))
        ) \
        .page.keyboard.press('F5') # без перезагрузки страницы получаем старые данные

        account_transactions_sender = api_manager.database_steps.get_transactions_by_account_id(sender_account.id)
        account_transactions_receiver = api_manager.database_steps.get_transactions_by_account_id(receiver_account.id)

        TransactionAssertions.has_transaction_with_amount(
            account_transactions_sender,
            TransactionType.TRANSFER_OUT,
            float(amount)
        )

        TransactionAssertions.has_transaction_with_amount(
            account_transactions_receiver,
            TransactionType.TRANSFER_IN,
            float(amount)
        )

    @pytest.mark.user_session(2)
    @pytest.mark.parametrize(
        argnames = 'amount, error_text',
        argvalues = [
            ("10000.01", BankAlert.MAX_AMOUNT_TRANSFER),
            ("-1", BankAlert.MIN_AMOUNT_TRANSFER),
        ]
    )
    def test_transfer_invalid_amount(
            self,
            api_manager: ApiManager,
            page: Page,
            user_request: CreateUserRequest,
            created_account_factory,
            error_text: str,
            amount: str,
    ):
        sender = SessionStorage.get_user(0)
        receiver = SessionStorage.get_user(1)

        sender, sender_account = created_account_factory(user=sender, balance=10000)
        receiver, receiver_account = created_account_factory(user=receiver)

        MakeTransfer(page).open() \
        .check_page_is_visible() \
        .select_account(str(sender_account.id)) \
        .recipient_name(receiver.username) \
        .recipient_account_number(str(receiver_account.accountNumber)) \
        .enter_amount(amount) \
        .confirm_check_click() \
        .send_transfer_and_check_msg(error_text)

        account_transactions_sender = api_manager.database_steps.get_transactions_by_account_id(sender_account.id)

        TransactionAssertions.has_no_transaction_by_type(
            account_transactions_sender,
            TransactionType.TRANSFER_OUT
        )

    @pytest.mark.user_session(2)
    def test_transfer_below_balance(
            self,
            api_manager: ApiManager,
            page: Page,
            user_request: CreateUserRequest,
            created_account_factory,
    ):
        sender = SessionStorage.get_user(0)
        receiver = SessionStorage.get_user(1)

        sender, sender_account = created_account_factory(user=sender, balance=2000)
        receiver, receiver_account = created_account_factory(user=receiver)

        MakeTransfer(page).open() \
        .check_page_is_visible() \
        .select_account(str(sender_account.id)) \
        .recipient_name(receiver.username) \
        .recipient_account_number(str(receiver_account.accountNumber)) \
        .enter_amount("3000") \
        .confirm_check_click() \
        .send_transfer_and_check_msg(BankAlert.INSUFFICIENT_FUNDS_OR_INVALID_ACCOUNTS_TRANSFER)

        account_transactions_sender = api_manager.database_steps.get_transactions_by_account_id(sender_account.id)

        TransactionAssertions.has_no_transaction_by_type(
            account_transactions_sender,
            TransactionType.TRANSFER_OUT
        )

    @pytest.mark.user_session(1)
    def test_transfer_empty_form(
            self,
            api_manager: ApiManager,
            page: Page,
            user_request: CreateUserRequest,
            created_account_factory,
    ):
        sender = SessionStorage.get_user(0)
        sender, sender_account = created_account_factory(user=sender)

        MakeTransfer(page).open() \
        .check_page_is_visible() \
        .send_transfer_and_check_msg(BankAlert.FILL_ALL_FIELDS_TRANSFER)

        account_transactions_sender = api_manager.database_steps.get_transactions_by_account_id(sender_account.id)

        TransactionAssertions.has_no_transaction_by_type(
            account_transactions_sender,
            TransactionType.TRANSFER_OUT
        )
