from dataclasses import dataclass
from enum import Enum
from typing import List

from src.main.api.models.create_account_response import CreateAccountResponse
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.create_user_response import CreateUserResponse
from src.main.api.models.get_profile_response import GetProfileResponse
from src.main.api.models.increase_deposit_request import IncreaseDepositRequest
from src.main.api.models.increase_deposit_response import IncreaseDepositResponse
from src.main.api.models.login_user_request import LoginUserRequest
from src.main.api.models.login_user_response import LoginUserResponse
from src.main.api.models.base_model import BaseModel
from src.main.api.models.transfer_request import TransferRequest
from src.main.api.models.transfer_response import TransferResponse
from src.main.api.models.update_profile_request import UpdateProfileRequest
from src.main.api.models.update_profile_response import UpdateProfileResponse


@dataclass(frozen=True)
class EndpointConfig:
    url: str
    request_model: BaseModel
    response_model: BaseModel


class Endpoint(Enum):
    ADMIN_CREATE_USER = EndpointConfig(
        url='/admin/users',
        request_model=CreateUserRequest,
        response_model=CreateUserResponse
    )

    ADMIN_DELETE_USER = EndpointConfig(
        url='/admin/users',
        request_model=None,
        response_model=None
    )

    ADMIN_GET_ALL_USERS = EndpointConfig(
        url='/admin/users',
        request_model=None,
        response_model=List[CreateUserRequest]
    )

    LOGIN_USER = EndpointConfig(
        url='/auth/login',
        request_model=LoginUserRequest,
        response_model=LoginUserResponse
    )

    CREATE_ACCOUNT = EndpointConfig(
        url='/accounts',
        request_model=None,
        response_model=CreateAccountResponse
    )

    GET_CUSTOMER_ACCOUNTS = EndpointConfig(
        url='/customer/accounts',
        request_model=None,
        response_model=List[CreateAccountResponse]
    )

    ACCOUNTS_DEPOSIT = EndpointConfig(
        url='/accounts/deposit',
        request_model=IncreaseDepositRequest,
        response_model=IncreaseDepositResponse
    )

    TRANSFER = EndpointConfig(
        url='/accounts/transfer',
        request_model=TransferRequest,
        response_model=TransferResponse
    )

    CUSTOMER_UPDATE_PROFILE = EndpointConfig(
        url='/customer/profile',
        request_model=UpdateProfileRequest,
        response_model=UpdateProfileResponse
    )

    CUSTOMER_GET_PROFILE = EndpointConfig(
        url='/customer/profile',
        request_model=None,
        response_model=GetProfileResponse
    )
