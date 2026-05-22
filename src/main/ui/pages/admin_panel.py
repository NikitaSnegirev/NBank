from src.main.ui.pages.base_page import BasePage


class AdminPanel(BasePage):
    @property
    def admin_panel_text(self):
        return self.page.get_by_text("Admin Panel")

    @property
    def add_user_button(self):
        return self.page.get_by_role("button", name="Add User")

    def url(self):
        return "/admin"

    def create_user(self, username: str, password: str):
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.add_user_button.click()
        return self

    def get_all_users(self):
        return self.page.locator(".card.shadow-custom:has(:has-text('All Users')) li")

