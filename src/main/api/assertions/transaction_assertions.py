from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.increase_deposit_response import TransactionResponse
from src.main.api.models.transaction_type import TransactionType


class TransactionAssertions:
    @staticmethod
    def has_no_transactions(api_manager: ApiManager, user_request: CreateUserRequest, account_id: int):
        transactions = api_manager.manage_user_accounts_steps.get_transactions(user_request, account_id)
        assert not transactions

    @staticmethod
    def get_transaction_by_type(
        transactions: list[TransactionResponse],
        transaction_type: TransactionType
    ) -> TransactionResponse | None:
        return next(
            (
                transaction
                for transaction in transactions
                if transaction.type == transaction_type
            ),
            None
        )

    @staticmethod
    def has_transaction_with_amount(
        transactions: list[TransactionResponse],
        transaction_type: TransactionType,
        amount: float
    ):
        transaction = TransactionAssertions.get_transaction_by_type(
            transactions,
            transaction_type
        )

        assert transaction is not None
        assert transaction.amount == amount

    @staticmethod
    def has_no_transaction_by_type(
        transactions: list[TransactionResponse],
        transaction_type: TransactionType
    ):
        transaction = TransactionAssertions.get_transaction_by_type(
            transactions,
            transaction_type
        )

        assert transaction is None
