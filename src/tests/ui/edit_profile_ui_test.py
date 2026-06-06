import pytest
from playwright.sync_api import Page, expect

from src.main.api.classes.api_manager import ApiManager
from src.main.api.generators.random_model_generator import RandomModelGenerator
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.update_profile_request import UpdateProfileRequest
from src.main.ui.pages.bank_alert import BankAlert
from src.main.ui.pages.user_dashboard import UserDashboard


@pytest.mark.ui
class TestEditProfile:
    @pytest.mark.check_name_change(new_name="John Smith")
    @pytest.mark.user_session(1)
    def test_update_name_in_the_profile(
            self,
            api_manager: ApiManager,
            page: Page,
            user_request: CreateUserRequest,
    ):
        dashboard_page = UserDashboard(page).open()
        expect(dashboard_page.welcome_text).to_be_visible()

        edit_profile = dashboard_page.profile()
        expect(edit_profile.edit_profile_header).to_be_visible()
        edit_profile.enter_new_name("John Smith")
        edit_profile.save_changes_click_and_check_msg(BankAlert.UPDATED_SUCCESSFULLY_NAME)

        assert api_manager.customer_management_steps.get_profile(user_request).name == "John Smith"

    @pytest.mark.user_session(1)
    @pytest.mark.check_name_change(new_name=None)
    def test_update_profile_bad_name(
            self,
            api_manager: ApiManager,
            page: Page,
            user_request: CreateUserRequest,
    ):
        dashboard_page = UserDashboard(page).open()
        expect(dashboard_page.welcome_text).to_be_visible()

        edit_profile = dashboard_page.profile()
        expect(edit_profile.edit_profile_header).to_be_visible()
        edit_profile.enter_new_name("JohnSmith")
        edit_profile.save_changes_click_and_check_msg(BankAlert.UPDATED_UNSUCCESSFULLY_NAME)

        assert api_manager.customer_management_steps.get_profile(user_request).name is None