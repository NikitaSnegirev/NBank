from src.main.api.models.comparison.model_assertions import ModelAssertions
from src.main.api.models.create_account_response import CreateAccountResponse
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.create_user_response import CreateUserResponse
from src.main.api.models.deposit_request import DepositRequest
from src.main.api.models.deposit_response import DepositResponse
from src.main.api.models.login_user_request import LoginUserRequest
from src.main.api.models.login_user_response import LoginUserResponse
from src.main.api.models.transfer_request import TransferRequest
from src.main.api.models.transfer_response import TransferResponse
from src.main.api.requests.skeleton.endpoint import Endpoint
from src.main.api.requests.skeleton.requesters.crud_requester import CrudRequester
from src.main.api.requests.skeleton.requesters.validated_crud_requester import ValidatedCrudRequester
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseError, ResponseSpecs
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

    def get_all_accounts(self, user_request: CreateUserRequest) -> list[CreateAccountResponse]:
        user_accounts: list[CreateAccountResponse] = ValidatedCrudRequester(
            RequestSpecs.auth_as_user(user_request.username, user_request.password),
            Endpoint.GET_CUSTOMER_ACCOUNTS,
            ResponseSpecs.request_returns_ok()
        ).get()

        return user_accounts

    def get_profile(self, user_request: CreateUserRequest) -> CreateUserResponse:
        user_profile: CreateUserResponse = ValidatedCrudRequester(
            RequestSpecs.auth_as_user(user_request.username, user_request.password),
            Endpoint.CUSTOMER_GET_PROFILE,
            ResponseSpecs.request_returns_ok()
        ).get()

        return user_profile

    def transfer_with_fraud_check(
            self,
            user_request: CreateUserRequest,
            transfer_request: TransferRequest,
    ) -> TransferResponse:
        transfer_response: TransferResponse = ValidatedCrudRequester(
            RequestSpecs.auth_as_user(user_request.username, user_request.password),
            Endpoint.TRANSFER_WITH_FRAUD_CHECK,
            ResponseSpecs.request_returns_ok()
        ).post(transfer_request)
        return transfer_response

    def transfer_with_fraud_check_invalid_data(
            self,
            user_request: CreateUserRequest,
            transfer_request: TransferRequest,
            error_text: ResponseError | str,
    ):
        CrudRequester(
            RequestSpecs.auth_as_user(user_request.username, user_request.password),
            Endpoint.TRANSFER_WITH_FRAUD_CHECK,
            ResponseSpecs.request_returns_bad_request_with_text(error_text)
        ).post(transfer_request)
