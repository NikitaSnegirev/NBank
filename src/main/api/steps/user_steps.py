from src.main.api.classes import api_manager
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.generators.random_model_generator import RandomModelGenerator
from src.main.api.models.comparison.model_assertions import ModelAssertions
from src.main.api.models.increase_deposit_request import IncreaseDepositRequest
from src.main.api.requests.skeleton.requesters.validated_crud_requester import ValidatedCrudRequester
from src.main.api.models.create_user_response import CreateUserResponse
from src.main.api.requests.skeleton.endpoint import Endpoint
from src.main.api.requests.skeleton.requesters.crud_requester import CrudRequester
from src.main.api.steps.base_steps import BaseSteps
from src.main.api.models.login_user_request import LoginUserRequest
from src.main.api.models.login_user_response import LoginUserResponse
from src.main.api.models.create_account_response import CreateAccountResponse
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs


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

    def increase_deposit(self, user_request: CreateUserRequest, id: int, balance: int):
        increase_deposit_request = IncreaseDepositRequest(
            id=id,
            balance=balance
        )
        CrudRequester(
            RequestSpecs.auth_as_user(user_request.username, user_request.password),
            Endpoint.ACCOUNTS_DEPOSIT,
            ResponseSpecs.request_returns_ok()
        ).post(increase_deposit_request)

    def increase_deposit_over_limit(self, user_request: CreateUserRequest, id: int, balance: int, error_text: str):
        increase_deposit_request = IncreaseDepositRequest(
            id=id,
            balance=balance
        )
        CrudRequester(
            RequestSpecs.auth_as_user(user_request.username, user_request.password),
            Endpoint.ACCOUNTS_DEPOSIT,
            ResponseSpecs.request_returns_bad_request_with_text(error_text)
        ).post(increase_deposit_request)