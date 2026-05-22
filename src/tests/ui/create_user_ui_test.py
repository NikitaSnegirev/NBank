import re

import pytest
from playwright.sync_api import expect, Page, Dialog

from src.main.api.classes.api_manager import ApiManager
from src.main.api.generators.random_model_generator import RandomModelGenerator
from src.main.api.models.comparison.model_assertions import ModelAssertions
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.ui.pages.admin_panel import AdminPanel
from src.main.ui.pages.bank_alert import BankAlert
from src.tests.ui.base_test import BaseUITest


@pytest.mark.ui
class TestCreateUser(BaseUITest):
    def test_admin_can_create_user(self, page: Page, admin_user_request: CreateUserRequest, api_manager: ApiManager):
        self.auth_as_user(page, admin_user_request)

        new_user_request: CreateUserRequest = RandomModelGenerator.generate(CreateUserRequest)

        admin_page = AdminPanel(page).open()\
        .create_user(new_user_request.username, new_user_request.password)\
        .check_alert_message_and_accept(BankAlert.USER_CREATED_SUCCESSFULLY)

        expect(admin_page.admin_panel_text).to_be_visible()
        expect(admin_page.get_all_users().filter(has_text=re.compile(rf"^{re.escape(new_user_request.username)}(\s+|.*)USER$", re.IGNORECASE))).to_be_visible()

        created_user = next(
            u for u in api_manager.admin_steps.get_all_users()
            if u.username == new_user_request.username
        )

        ModelAssertions(created_user, new_user_request).match()

    def test_admin_cannot_create_user_with_invalid_data(self, page: Page, admin_user_request: CreateUserRequest, api_manager: ApiManager):
        # ШАГ 1: админ залогинился в банке
        self.auth_as_user(page, admin_user_request)

        # ШАГ 2: создание пользователя c невалидным username
        new_user_request: CreateUserRequest = RandomModelGenerator.generate(CreateUserRequest)
        new_user_request.username = "a"

        admin_page = AdminPanel(page).open()
        expect(admin_page.admin_panel_text).to_be_visible()

        admin_page = admin_page.create_user(new_user_request.username, new_user_request.password)
        admin_page.check_alert_message_and_accept(BankAlert.USERNAME_MUST_BE_BETWEEN_3_AND_15_CHARACTERS)
        expect(admin_page.get_all_users().filter(has_text=re.compile(rf"^{re.escape(new_user_request.username)}(\s+|.*)USER$", re.IGNORECASE))).to_have_count(0)

        # ШАГ 3: проверка, что юзер НЕ создан на API
        assert not any(u.username == new_user_request.username for u in api_manager.admin_steps.get_all_users())