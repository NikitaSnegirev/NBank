import json

import requests
from playwright.sync_api import expect

from src.main.api.configs.config import Config
from src.main.ui.pages.base_page import BasePage


class MakeTransfer(BasePage):
    def open(self):
        self.normalize_customer_accounts_response()
        return super().open()

    @property
    def make_transfer_header(self):
        return self.page.get_by_text("🔄 Make a Transfer")

    @property
    def your_account_selector(self):
        return self.page.locator(".form-control.account-selector")

    @property
    def recipient_name_input(self):
        return self.page.get_by_placeholder("Enter recipient name")

    @property
    def recipient_account_number_input(self):
        return self.page.get_by_placeholder("Enter recipient account number")

    @property
    def enter_amount_input(self):
        return self.page.get_by_placeholder("Enter amount")

    @property
    def send_transfer_button(self):
        return self.page.get_by_role("button", name="🚀 Send Transfer")

    def select_account(self, number_account: str):
        self.your_account_selector.select_option(number_account)
        return self

    def recipient_name(self, recipient_name: str):
        self.recipient_name_input.fill(recipient_name)
        return self

    def recipient_account_number(self, recipient_account_number: str):
        self.recipient_account_number_input.fill(recipient_account_number)
        return self

    def enter_amount(self, enter_amount: str):
        self.enter_amount_input.fill(enter_amount)
        return self

    def confirm_check_click(self):
        self.page.locator("#confirmCheck").click()
        return self

    def normalize_customer_accounts_response(self):
        def _handler(route):
            request = route.request
            if request.method.upper() != "GET":
                route.continue_()
                return

            auth_header = request.headers.get("authorization")
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
            if auth_header:
                headers["Authorization"] = auth_header

            response = requests.get(
                url=f"{Config.get('server')}{Config.get('api_version')}/customer/accounts",
                headers=headers,
                timeout=10,
            )
            body = response.text
            content_type = response.headers.get("content-type", "application/json")

            if response.ok:
                accounts = response.json()
                if isinstance(accounts, list):
                    for account in accounts:
                        account.setdefault("transactions", [])
                    body = json.dumps(accounts)
                    content_type = "application/json"

            route.fulfill(
                status=response.status_code,
                headers={"content-type": content_type},
                body=body,
            )

        self.page.route("**/customer/accounts", _handler)
        return self

    def send_transfer_and_check_msg(self, expected_alert: str):
        return self.click_and_accept_alert(self.send_transfer_button, expected_alert)

    def check_page_is_visible(self):
        expect(self.make_transfer_header).to_be_visible()
        return self

    def url(self):
        return "/transfer"
