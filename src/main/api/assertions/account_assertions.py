from decimal import Decimal

from src.main.api.classes.api_manager import ApiManager


class AccountAssertions:
    @staticmethod
    def get_balance(api_manager: ApiManager, account_number: str) -> Decimal:
        account_dao = api_manager.database_steps.get_account_by_account_number(account_number)
        return Decimal(str(account_dao.balance))

    @staticmethod
    def balances_changed_by_transfer(
        api_manager: ApiManager,
        sender_account_number: str,
        receiver_account_number: str,
        sender_balance_before: Decimal,
        receiver_balance_before: Decimal,
        transfer_amount: float,
    ):
        amount = Decimal(str(transfer_amount))
        assert AccountAssertions.get_balance(api_manager, sender_account_number) == sender_balance_before - amount
        assert AccountAssertions.get_balance(api_manager, receiver_account_number) == receiver_balance_before + amount

    @staticmethod
    def balances_unchanged(
        api_manager: ApiManager,
        sender_account_number: str,
        receiver_account_number: str,
        sender_balance_before: Decimal,
        receiver_balance_before: Decimal,
    ):
        assert AccountAssertions.get_balance(api_manager, sender_account_number) == sender_balance_before
        assert AccountAssertions.get_balance(api_manager, receiver_account_number) == receiver_balance_before
