from src.main.ui.pages.base_page import BasePage
from src.main.ui.pages.deposit_money import DepositMoney
from src.main.ui.pages.make_transfer import MakeTransfer
from src.main.ui.pages.edit_profile import EditProfile


class UserDashboard(BasePage):
    @property
    def welcome_text(self):
        return self.page.get_by_text("User Dashboard")

    @property
    def create_new_account_button(self):
        return self.page.get_by_role("button", name="➕ Create New Account")

    @property
    def deposit_money_button(self):
        return self.page.get_by_role("button", name="💰 Deposit Money")

    @property
    def make_transfer_button(self):
        return self.page.get_by_role("button", name="🔄 Make a Transfer")

    @property
    def profile_button(self):
        return self.page.locator(".user-info")

    def url(self):
        return "/dashboard"

    def create_new_account(self):
        self.create_new_account_button.click()
        return self

    def deposit_money(self):
        self.deposit_money_button.click()
        return self.get_page(DepositMoney)

    def make_transfer(self):
        self.make_transfer_button.click()
        return self.get_page(MakeTransfer)

    def profile(self):
        self.profile_button.click()
        return self.get_page(EditProfile)