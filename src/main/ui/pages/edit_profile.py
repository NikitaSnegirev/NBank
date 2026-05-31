from src.main.ui.pages.base_page import BasePage


class EditProfile(BasePage):

    @property
    def edit_profile_header(self):
        return self.page.get_by_text("✏️ Edit Profile")

    @property
    def enter_new_name_input(self):
        return self.page.get_by_placeholder("Enter new name")

    @property
    def save_changes(self):
        return self.page.get_by_role("button", name="💾 Save Changes")

    def enter_new_name(self, new_name: str):
        self.enter_new_name_input.fill(new_name)
        return self

    def save_changes_click_and_check_msg(self, expected_alert: str):
        self.check_alert_message_and_accept(expected_alert)
        self.save_changes.click()
        return self

    def url(self):
        return "/edit-profile"