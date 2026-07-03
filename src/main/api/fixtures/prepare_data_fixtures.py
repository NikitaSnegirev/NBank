from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.classes.session_storage import SessionStorage
from src.main.api.generators.random_model_generator import RandomModelGenerator
from src.main.api.models.create_account_response import CreateAccountResponse
from src.main.api.models.create_user_request import CreateUserRequest


@dataclass(frozen=True)
class PreparedUserAccount:
    user: CreateUserRequest
    account: CreateAccountResponse


def _get_int_kw(mark: pytest.Mark, key: str, default: int) -> int:
    try:
        return int(mark.kwargs.get(key, default))
    except Exception:
        return int(default)


def _get_optional_float_kw(mark: pytest.Mark, key: str) -> Optional[float]:
    val = mark.kwargs.get(key)
    if val is None:
        return None
    try:
        return float(val)
    except Exception:
        return None


@pytest.fixture(scope="function")
def prepared_users(
    request: pytest.FixtureRequest,
    api_manager: ApiManager,
    clear_storage,
) -> list[CreateUserRequest]:
    """
    Prepare N users via admin API.
    Controlled by marker: @pytest.mark.prepare_users(number=2)
    """
    mark = request.node.get_closest_marker("prepare_users")
    if not mark:
        return []

    n = _get_int_kw(mark, "number", 1)
    if n <= 0:
        return []

    users: list[CreateUserRequest] = []
    for _ in range(n):
        user = RandomModelGenerator.generate(CreateUserRequest)
        api_manager.admin_steps.create_user(user)
        users.append(user)

    SessionStorage.add_users(users)
    return users


@pytest.fixture(scope="function")
def prepared_user_accounts(
    request: pytest.FixtureRequest,
    api_manager: ApiManager,
    prepared_users: list[CreateUserRequest],
) -> list[PreparedUserAccount]:
    """
    Prepare N accounts for prepared users; optionally deposit the same amount to each.
    Controlled by marker: @pytest.mark.prepare_accounts(number=2, deposit=5000)
    """
    mark = request.node.get_closest_marker("prepare_accounts")
    if not mark:
        return []

    n = _get_int_kw(mark, "number", 1)
    deposit = _get_optional_float_kw(mark, "deposit")

    if n <= 0:
        return []
    if not prepared_users:
        raise RuntimeError(
            "prepare_accounts requires prepared users. Add @pytest.mark.prepare_users(number=...) "
            "or provide users via prepared_users fixture."
        )

    result: list[PreparedUserAccount] = []

    for i in range(n):
        user = prepared_users[i % len(prepared_users)]
        account = api_manager.user_steps.create_account(user)
        if deposit is not None:
            api_manager.manage_user_accounts_steps.deposit(user, account.id, float(deposit))
        result.append(PreparedUserAccount(user=user, account=account))

    return result