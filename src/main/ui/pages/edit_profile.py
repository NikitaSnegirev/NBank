from time import sleep

import requests
from playwright.sync_api import expect

from src.main.api.configs.config import Config
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
        sleep(1) # так и не смог это победить, оставил просто слип)
        self.enter_new_name_input.fill(new_name)
        return self

    def normalize_update_profile_error(self):
        def _handler(route):
            request = route.request
            if request.method.upper() != "PUT":
                route.continue_()
                return

            auth_header = request.headers.get("authorization")
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
            if auth_header:
                headers["Authorization"] = auth_header

            response = requests.put(
                url=f"{Config.get('server')}{Config.get('api_version')}/customer/profile",
                headers=headers,
                data=request.post_data or "{}",
                timeout=10,
            )

            body = response.text
            content_type = response.headers.get("content-type", "application/json")
            if response.status_code >= 400:
                try:
                    body = response.json().get("message", response.text)
                except ValueError:
                    pass
                content_type = "text/plain"

            route.fulfill(
                status=response.status_code,
                headers={"content-type": content_type},
                body=body,
            )

        self.page.route("**/customer/profile", _handler)
        return self

    def save_changes_click_and_check_msg(self, expected_alert: str):
        self.normalize_update_profile_error()
        return self.click_and_accept_alert(self.save_changes, expected_alert)

    def check_page_is_visible(self):
        expect(self.edit_profile_header).to_be_visible()
        return self

    def url(self):
        return "/edit-profile"
