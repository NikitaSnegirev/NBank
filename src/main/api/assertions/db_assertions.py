from src.main.api.classes.api_manager import ApiManager

class DbAssertions:
    @staticmethod
    def has_no_transactions_by_related_account_id(api_manager: ApiManager, related_account_id: int):
        transaction_dao = api_manager.database_steps.find_transactions_by_related_account_id(related_account_id)

        assert transaction_dao is None, (
            f"Transaction should NOT exist in DB for related_account_id={related_account_id}, "
            f"but was found: {transaction_dao}"
        )
