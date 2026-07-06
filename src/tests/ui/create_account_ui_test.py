import pytest
from playwright.sync_api import Page

from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.ui.pages.user_dashboard import UserDashboard


@pytest.mark.ui
@pytest.mark.usefixtures("admin_session_autologin", "browser_match_guard")
class TestCreateAccount:
    @pytest.mark.user_session(10)
    @pytest.mark.check_accounts_change(delta=1)
    def test_user_can_create_account(self, api_manager: ApiManager, page: Page, user_request: CreateUserRequest):
        UserDashboard(page).open() \
        .check_page_is_visible() \
        .create_new_account()

        accounts = api_manager.user_steps.get_all_accounts(user_request)
        assert len(accounts) == 1
        assert accounts[0].balance == 0
