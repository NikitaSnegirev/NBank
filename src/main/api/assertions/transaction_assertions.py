from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.create_user_request import CreateUserRequest


class TransactionAssertions:
    @staticmethod
    def has_no_transactions(api_manager: ApiManager, user_request: CreateUserRequest, account_id: int):
        transactions = api_manager.manage_user_accounts_steps.get_transactions(user_request, account_id)
        assert not transactions