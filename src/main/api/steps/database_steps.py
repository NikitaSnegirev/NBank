from __future__ import annotations

from typing import Optional

from src.main.api.database.dao.customer_dao import CustomerDao
from src.main.api.database.dao.transactions_dao import TransactionsDao
from src.main.api.database.db_client import Condition, DBRequest, RequestType, fetch_all
from src.main.api.database.dao.user_dao import UserDao
from src.main.api.database.dao.account_dao import AccountDao


class DataBaseSteps:
    @staticmethod
    def get_user_by_username(username: str) -> UserDao:
        return (
            DBRequest.builder()
            .request_type(RequestType.SELECT)
            .table("customers")
            .where(Condition.equal_to("username", username))
            .extract_as(UserDao)
        )

    @staticmethod
    def find_user_by_username(username: str) -> Optional[UserDao]:
        return (
            DBRequest.builder()
            .request_type(RequestType.SELECT)
            .table("customers")
            .where(Condition.equal_to("username", username))
            .extract_optional_as(UserDao)
        )

    @staticmethod
    def get_account_by_account_number(account_number: str) -> AccountDao:
        return (
            DBRequest.builder()
            .request_type(RequestType.SELECT)
            .table("accounts")
            .where(Condition.equal_to("account_number", account_number))
            .extract_as(AccountDao)
        )

    @staticmethod
    def find_account_by_account_number(account_number: str) -> Optional[AccountDao]:
        return (
            DBRequest.builder()
            .request_type(RequestType.SELECT)
            .table("accounts")
            .where(Condition.equal_to("account_number", account_number))
            .extract_optional_as(AccountDao)
        )

    @staticmethod
    def get_transactions_by_transaction_id(transaction_id: int) -> TransactionsDao:
        return (
            DBRequest.builder()
            .request_type(RequestType.SELECT)
            .table("transactions")
            .where(Condition.equal_to("id", transaction_id))
            .extract_as(TransactionsDao)
        )

    @staticmethod
    def get_transactions_by_account_id(account_id: int) -> list[TransactionsDao]:
        rows = fetch_all(
            """
            SELECT * FROM transactions
            WHERE account_id = %s OR related_account_id = %s
            ORDER BY id DESC
            """,
            (account_id, account_id),
        )
        return [TransactionsDao(**row) for row in rows]

    @staticmethod
    def find_transactions_by_related_account_id(related_account_id: int) -> Optional[TransactionsDao]:
        return (
            DBRequest.builder()
            .request_type(RequestType.SELECT)
            .table("transactions")
            .where(Condition.equal_to("related_account_id", related_account_id))
            .extract_optional_as(TransactionsDao)
        )

    @staticmethod
    def get_customer_by_customer_id(customer_id: int) -> CustomerDao:
        return (
            DBRequest.builder()
            .request_type(RequestType.SELECT)
            .table("customers")
            .where(Condition.equal_to("id", customer_id))
            .extract_as(CustomerDao)
        )
