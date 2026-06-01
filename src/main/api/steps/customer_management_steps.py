from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.get_profile_response import GetProfileResponse
from src.main.api.models.update_profile_request import UpdateProfileRequest
from src.main.api.models.update_profile_response import UpdateProfileResponse
from src.main.api.requests.skeleton.endpoint import Endpoint
from src.main.api.requests.skeleton.requesters.crud_requester import CrudRequester
from src.main.api.requests.skeleton.requesters.validated_crud_requester import ValidatedCrudRequester
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseError, ResponseSpecs
from src.main.api.steps.base_steps import BaseSteps


class CustomerManagementSteps(BaseSteps):

    def update_profile(self, user_request: CreateUserRequest, name: str) -> UpdateProfileResponse:
        update_profile_request = UpdateProfileRequest(
            name=name
        )
        update_profile: UpdateProfileResponse = ValidatedCrudRequester(
            RequestSpecs.auth_as_user(user_request.username, user_request.password),
            Endpoint.CUSTOMER_UPDATE_PROFILE,
            ResponseSpecs.profile_updated_successfully()
        ).put(update_profile_request)
        return update_profile

    def get_profile(self, user_request: CreateUserRequest) -> GetProfileResponse:
        get_profile: GetProfileResponse = ValidatedCrudRequester(
            RequestSpecs.auth_as_user(user_request.username, user_request.password),
            Endpoint.CUSTOMER_GET_PROFILE,
            ResponseSpecs.request_returns_ok()
        ).get()

        return get_profile

    def update_profile_bad_name(self, user_request: CreateUserRequest, name: str, error_text: ResponseError):
        update_profile_request = UpdateProfileRequest(
            name=name
        )
        CrudRequester(
            RequestSpecs.auth_as_user(user_request.username, user_request.password),
            Endpoint.CUSTOMER_UPDATE_PROFILE,
            ResponseSpecs.request_returns_bad_request_with_text(error_text)
        ).put(update_profile_request)
