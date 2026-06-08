from __future__ import annotations

from typing import Any, Optional

import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.create_user_request import CreateUserRequest


def _resolve_source(request: pytest.FixtureRequest, source: str) -> Any:
    """
    Resolve "fixture_or_param.attr1.attr2" into a concrete value.
    Examples:
      - "username" -> request.getfixturevalue("username")
      - "create_user_request.username" -> request.getfixturevalue("create_user_request").username
    """
    parts = [p for p in source.split(".") if p]
    if not parts:
        raise ValueError("username_source is empty")

    root = parts[0]

    # Parametrized values live in callspec.params (not always accessible via getfixturevalue on teardown).
    callspec = getattr(request.node, "callspec", None)
    if callspec is not None and root in getattr(callspec, "params", {}):
        value = callspec.params[root]
    else:
        # Fixture values
        value = request.getfixturevalue(root)

    for attr in parts[1:]:
        value = getattr(value, attr)
    return value


@pytest.fixture(autouse=True, scope="function")
def entity_will_be_created(request: pytest.FixtureRequest):
    """
    Marker-driven helper for cleanup: adds entity/entities to `created_objects`.

    Use in UI tests where creation happens via UI (not via API steps), so the cleanup list
    wouldn't be populated automatically.

    Examples:
      @pytest.mark.entity_will_be_created("new_user_request")
      @pytest.mark.entity_will_be_created("some_fixture.attr")
    """
    mark = request.node.get_closest_marker("entity_will_be_created")
    if not mark:
        yield
        return

    api_manager: ApiManager = request.getfixturevalue("api_manager")

    sources = list(mark.args or [])
    source_kw = mark.kwargs.get("source")
    if source_kw:
        sources.append(source_kw)

    if not sources:
        raise ValueError("entity_will_be_created requires at least one source (e.g. 'new_user_request')")

    for src in sources:
        entity = _resolve_source(request, str(src)) if isinstance(src, str) else src
        api_manager.admin_steps.created_objects.append(entity)

    yield


@pytest.fixture(autouse=True, scope="function")
def check_all_users_change(request: pytest.FixtureRequest, created_objects):
    """
    Marker-driven post-action verification for API tests.

    Usage:
      @pytest.mark.check_all_users_change(delta=1, username_source="create_user_request.username")
      @pytest.mark.check_all_users_change(delta=0, username_source="username")
    """
    mark = request.node.get_closest_marker("check_all_users_change")
    if not mark:
        yield
        return

    delta = int(mark.kwargs.get("delta", 0))
    username_source: Optional[str] = mark.kwargs.get("username_source")
    should_exist = mark.kwargs.get("should_exist")
    if should_exist is None:
        should_exist = delta > 0
    should_exist = bool(should_exist)

    # In xdist (or other parallel runs) global "count delta" is not stable, because other tests
    # can create/delete users between our before/after snapshots. Allow opting into strict mode.
    strict_delta = bool(mark.kwargs.get("strict_delta", False))
    running_xdist = hasattr(request.config, "workerinput")

    api_manager: ApiManager = request.getfixturevalue("api_manager")

    # Resolve username early (before yield), while parametrized args are still accessible.
    resolved_username: Optional[str] = None
    if username_source:
        resolved_username = str(_resolve_source(request, username_source))

    before = api_manager.admin_steps.get_all_users()
    before_usernames = {u.username for u in before}
    yield
    after = api_manager.admin_steps.get_all_users()
    after_usernames = {u.username for u in after}

    if resolved_username is not None:
        if should_exist:
            assert resolved_username in after_usernames, (
                f"Expected user '{resolved_username}' existence=True via GET /admin/users, "
                f"but it was not found."
            )
            # In sequential runs we can also assert the user wasn't present before (true "creation").
            if (not running_xdist) and delta > 0:
                assert resolved_username not in before_usernames, (
                    f"Expected user '{resolved_username}' to be newly created, but it already existed before."
                )
        else:
            assert resolved_username not in after_usernames, (
                f"Expected user '{resolved_username}' existence=False via GET /admin/users, "
                f"but it was found."
            )

    # Count delta is reliable only in sequential runs (or when explicitly requested).
    if strict_delta and not running_xdist:
        assert len(after) - len(before) == delta, (
            f"Expected users delta={delta} (after-before), but got {len(after) - len(before)}. "
            f"before={len(before)}, after={len(after)}"
        )


@pytest.fixture(autouse=True, scope="function")
def check_accounts_change(request: pytest.FixtureRequest):
    """
    Marker-driven post-action verification for accounts (customer accounts list).

    Usage:
      @pytest.mark.check_accounts_change(delta=1)
    """
    mark = request.node.get_closest_marker("check_accounts_change")
    if not mark:
        yield
        return

    delta = int(mark.kwargs.get("delta", 0))

    # UI tests: ensure @pytest.mark.user_session(...) autouse hook ran BEFORE we snapshot accounts.
    # Otherwise SessionStorage may be empty/cleared and `user_request` may refer to a different user
    # than the one logged-in in UI, causing false delta=0.
    if request.node.get_closest_marker("user_session") is not None:
        try:
            request.getfixturevalue("user_session_extension")
        except Exception:
            # In non-UI contexts this fixture may not exist; ignore.
            pass

    api_manager: ApiManager = request.getfixturevalue("api_manager")
    user_request: CreateUserRequest = request.getfixturevalue("user_request")

    before = api_manager.user_steps.get_all_accounts(user_request)

    yield

    after = api_manager.user_steps.get_all_accounts(user_request)

    assert len(after) - len(before) == delta, (
        f"Expected accounts delta={delta} (after-before), but got {len(after) - len(before)}. "
        f"before={len(before)}, after={len(after)}"
    )

@pytest.fixture(autouse=True, scope="function")
def check_name_change(request: pytest.FixtureRequest):
    mark = request.node.get_closest_marker("check_name_change")
    if not mark:
        yield
        return

    missing = object()

    new_name = mark.kwargs.get("new_name", missing)
    new_name_source = mark.kwargs.get("new_name_source")

    if new_name_source is not None:
        new_name = _resolve_source(request, new_name_source)

    if request.node.get_closest_marker("user_session") is not None:
        try:
            request.getfixturevalue("user_session_extension")
        except Exception:
            # In non-UI contexts this fixture may not exist; ignore.
            pass

    api_manager: ApiManager = request.getfixturevalue("api_manager")
    user_request: CreateUserRequest = request.getfixturevalue("user_request")

    yield

    actual_name = api_manager.customer_management_steps.get_profile(user_request).name
    assert actual_name == new_name , (
        f"Expected name={new_name}, but got {actual_name}."
    )

@pytest.fixture(autouse=True, scope="function")
def check_transactions_change(request: pytest.FixtureRequest):
    mark = request.node.get_closest_marker("check_transactions_change")
    if not mark:
        yield
        return

    account_source = mark.kwargs.get("account_source")
    user_source = mark.kwargs.get("user_source", "user_request")


    delta = int(mark.kwargs.get("delta", 0))

    if request.node.get_closest_marker("user_session") is not None:
        try:
            request.getfixturevalue("user_session_extension")
        except Exception:
            # In non-UI contexts this fixture may not exist; ignore.
            pass

    api_manager: ApiManager = request.getfixturevalue("api_manager")
    user_request: CreateUserRequest = _resolve_source(request, user_source)
    account = _resolve_source(request, account_source)

    before = api_manager.manage_user_accounts_steps.get_transactions(
        user_request,
        account.id,
    )

    yield

    after = api_manager.manage_user_accounts_steps.get_transactions(
        user_request,
        account.id,
    )

    actual_delta = len(after) - len(before)

    assert actual_delta == delta, (
        f"Expected transactions delta={delta}, but got {actual_delta}. "
        f"before={len(before)}, after={len(after)}, account_id={account.id}"
    )