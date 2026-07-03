from src.main.api.models.comparison.model_assertions import ModelAssertions
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.deposit_request import DepositRequest
from src.main.api.models.deposit_response import DepositResponse, TransactionResponse
from src.main.api.models.transfer_request import TransferRequest
from src.main.api.models.transfer_response import TransferResponse
from src.main.api.requests.skeleton.endpoint import Endpoint
from src.main.api.requests.skeleton.requesters.crud_requester import CrudRequester
from src.main.api.requests.skeleton.requesters.validated_crud_requester import ValidatedCrudRequester
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseError, ResponseSpecs
from src.main.api.steps.base_steps import BaseSteps


class ManageUserAccountsSteps(BaseSteps):

    def deposit(self, user_request: CreateUserRequest, id: int, balance: int) -> DepositResponse:
        deposit_request = DepositRequest(
            accountId=id,
            amount=balance,
        )
        deposit_response: DepositResponse = ValidatedCrudRequester(
            RequestSpecs.auth_as_user(user_request.username, user_request.password),
            Endpoint.ACCOUNTS_DEPOSIT,
            ResponseSpecs.request_returns_ok()
        ).post(deposit_request)

        ModelAssertions(deposit_request, deposit_response).match()
        assert deposit_response.transactionId

        return deposit_response


    def deposit_bad_request(self, user_request: CreateUserRequest, id: int, balance: int, error_text: ResponseError):
        deposit_request = DepositRequest(
            accountId=id,
            amount=balance,
        )
        CrudRequester(
            RequestSpecs.auth_as_user(user_request.username, user_request.password),
            Endpoint.ACCOUNTS_DEPOSIT,
            ResponseSpecs.request_returns_bad_request_with_text(error_text)
        ).post(deposit_request)

    def transfer(self, user_request: CreateUserRequest, transfer_request: TransferRequest) -> TransferResponse:
        transfer_response: TransferResponse = ValidatedCrudRequester(
            RequestSpecs.auth_as_user(user_request.username, user_request.password),
            Endpoint.TRANSFER,
            ResponseSpecs.transfer_successfully()
        ).post(transfer_request)

        ModelAssertions(transfer_request, transfer_response).match()

        return transfer_response

    def transfer_bad_request(self, user_request: CreateUserRequest, transfer_request: TransferRequest, error_text: ResponseError):
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
