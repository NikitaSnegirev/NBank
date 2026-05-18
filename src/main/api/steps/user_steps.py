from src.main.api.models.comparison.model_assertions import ModelAssertions
from src.main.api.models.create_account_response import CreateAccountResponse
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.increase_deposit_request import IncreaseDepositRequest
from src.main.api.models.increase_deposit_response import IncreaseDepositResponse
from src.main.api.models.login_user_request import LoginUserRequest
from src.main.api.models.login_user_response import LoginUserResponse
from src.main.api.models.transfer_request import TransferRequest
from src.main.api.models.transfer_response import TransferResponse
from src.main.api.requests.skeleton.endpoint import Endpoint
from src.main.api.requests.skeleton.requesters.crud_requester import CrudRequester
from src.main.api.requests.skeleton.requesters.validated_crud_requester import ValidatedCrudRequester
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs
from src.main.api.steps.base_steps import BaseSteps


class UserSteps(BaseSteps):
    def login(self, user_request: CreateUserRequest) -> LoginUserResponse:
        login_request = LoginUserRequest(username=user_request.username, password=user_request.password)
        login_response: LoginUserResponse = ValidatedCrudRequester(
            RequestSpecs.unauth_spec(),
            Endpoint.LOGIN_USER,
            ResponseSpecs.request_returns_ok()
        ).post(login_request)
        ModelAssertions(login_request, login_response).match()
        return login_response

    def create_account(self, user_request: CreateUserRequest) -> CreateAccountResponse:
        create_account_response: CreateAccountResponse = ValidatedCrudRequester(
            RequestSpecs.auth_as_user(user_request.username, user_request.password),
            Endpoint.CREATE_ACCOUNT,
            ResponseSpecs.entity_was_created()
        ).post()

        assert create_account_response.balance == 0.0
        assert not create_account_response.transactions
        return create_account_response

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

        assert increase_deposit_response.id == id
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

        assert transfer_response.receiverAccountId == receiver_account_id
        assert transfer_response.amount == amount
        assert transfer_response.message == "Transfer successful"
        assert transfer_response.senderAccountId == sender_account_id

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