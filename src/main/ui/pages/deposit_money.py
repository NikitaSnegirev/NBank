from playwright.sync_api import Page

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

    def deposit_click_and_check_msg(self, expected_alert: str):
        self.check_alert_message_and_accept(expected_alert)
        self.deposit_button.click()
        return self

    def url(self):
        return "/deposit"