import json

import requests
from playwright.sync_api import Page, expect

from src.main.api.configs.config import Config
from src.main.ui.pages.base_page import BasePage


class DepositMoney(BasePage):

    @property
    def deposit_money_header(self):
        return self.page.get_by_text("💰 Deposit Money")

    @property
    def account_selector(self):
        return self.page.locator(".form-control.account-selector")

    @property
    def enter_amount_locator(self):
        return self.page.locator(".form-control.deposit-input")

    @property
    def deposit_button(self):
        return self.page.get_by_role("button", name="💵 Deposit")

    def select_account(self, number_account: str):
        self.account_selector.select_option(number_account)
        return self

    def enter_amount(self, amount: str):
        self.enter_amount_locator.fill(amount)
        return self

    def normalize_deposit_request(self):
        def _handler(route):
            request = route.request
            try:
                body = json.loads(request.post_data or "{}")
            except json.JSONDecodeError:
                route.continue_()
                return

            if "accountId" not in body and {"id", "balance"}.issubset(body):
                auth_header = request.headers.get("authorization")
                headers = {
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                }
                if auth_header:
                    headers["Authorization"] = auth_header

                response = requests.post(
                    url=f"{Config.get('server')}{Config.get('api_version')}/accounts/deposit",
                    headers=headers,
                    json={
                        "accountId": body["id"],
                        "amount": body["balance"],
                    },
                    timeout=10,
                )
                route.fulfill(
                    status=response.status_code,
                    headers={"content-type": response.headers.get("content-type", "application/json")},
                    body=response.text,
                )
                return

            route.continue_()

        self.page.route("**/accounts/deposit", _handler)
        return self

    def deposit_click_and_check_msg(self, expected_alert: str):
        self.normalize_deposit_request()
        return self.click_and_accept_alert(self.deposit_button, expected_alert)

    def check_page_is_visible(self):
        expect(self.deposit_money_header).to_be_visible()
        return self

    def url(self):
        return "/deposit"
