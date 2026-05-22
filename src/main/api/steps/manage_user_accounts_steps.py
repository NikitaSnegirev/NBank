from src.main.api.models.comparison.model_assertions import ModelAssertions
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.increase_deposit_request import IncreaseDepositRequest
from src.main.api.models.increase_deposit_response import IncreaseDepositResponse, TransactionResponse
from src.main.api.models.transfer_request import TransferRequest
from src.main.api.models.transfer_response import TransferResponse
from src.main.api.requests.skeleton.endpoint import Endpoint
from src.main.api.requests.skeleton.requesters.crud_requester import CrudRequester
from src.main.api.requests.skeleton.requesters.validated_crud_requester import ValidatedCrudRequester
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs
from src.main.api.steps.base_steps import BaseSteps


class ManageUserAccountsSteps(BaseSteps):

    def increase_deposit(self, user_request: CreateUserRequest, id: int, balance: int) -> IncreaseDepositResponse:
        increase_deposit_request = IncreaseDepositRequest(
            id=id,
            balance=balance
        )
        increase_deposit_response: IncreaseDepositResponse = ValidatedCrudRequester(
            RequestSpecs.auth_as_user(user_request.username, user_request.password),
            Endpoint.ACCOUNTS_DEPOSIT,
            ResponseSpecs.request_returns_ok()
        ).post(increase_deposit_request)

        ModelAssertions(increase_deposit_request, increase_deposit_response).match()
        assert increase_deposit_response.transactions

        return increase_deposit_response


    def increase_deposit_bad_request(self, user_request: CreateUserRequest, id: int, balance: int, error_text: str):
        increase_deposit_request = IncreaseDepositRequest(
            id=id,
            balance=balance
        )
        CrudRequester(
            RequestSpecs.auth_as_user(user_request.username, user_request.password),
            Endpoint.ACCOUNTS_DEPOSIT,
            ResponseSpecs.request_returns_bad_request_with_text(error_text)
        ).post(increase_deposit_request)


    def transfer(self, user_request: CreateUserRequest, sender_account_id: int, receiver_account_id: int, amount: float) -> TransferResponse:
        transfer_request = TransferRequest(
            senderAccountId=sender_account_id,
            receiverAccountId=receiver_account_id,
            amount=amount
        )
        transfer_response: TransferResponse = ValidatedCrudRequester(
            RequestSpecs.auth_as_user(user_request.username, user_request.password),
            Endpoint.TRANSFER,
            ResponseSpecs.request_returns_ok()
        ).post(transfer_request)

        ModelAssertions(transfer_request, transfer_response).match()
        assert transfer_response.message == "Transfer successful"

        return transfer_response


    def transfer_bad_request(self, user_request: CreateUserRequest, sender_account_id: int, receiver_account_id: int, amount: float, error_text: str):
        transfer_request = TransferRequest(
            senderAccountId=sender_account_id,
            receiverAccountId=receiver_account_id,
            amount=amount
        )
        CrudRequester(
            RequestSpecs.auth_as_user(user_request.username, user_request.password),
            Endpoint.TRANSFER,
            ResponseSpecs.request_returns_bad_request_with_text(error_text)
        ).post(transfer_request)

    def get_transactions(self, user_request: CreateUserRequest, account_id: int) -> list[TransactionResponse]:
        transactions: list[TransactionResponse] = ValidatedCrudRequester(
            RequestSpecs.auth_as_user(user_request.username, user_request.password),
            Endpoint.GET_TRANSACTIONS,
            ResponseSpecs.request_returns_ok()
        ).get_transactions(account_id)

        return transactions
