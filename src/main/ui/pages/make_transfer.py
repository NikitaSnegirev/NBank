from src.main.ui.pages.base_page import BasePage


class MakeTransfer(BasePage):

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

    def send_transfer_and_check_msg(self, expected_alert: str):
        self.check_alert_message_and_accept(expected_alert)
        self.send_transfer_button.click()
        return self

    def url(self):
        return "/transfer"