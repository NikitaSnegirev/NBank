from src.main.ui.pages.base_page import BasePage


class LoginPage(BasePage):

    @property
    def login_button(self):
        return self.page.get_by_role("button", name="Login")

    def url(self):
        return "/login"

    def login(self, username: str, password: str):
        self.page.get_by_placeholder("Username").fill(username)
        self.page.get_by_placeholder("Password").fill(password)
        self.login_button.click()
        return self