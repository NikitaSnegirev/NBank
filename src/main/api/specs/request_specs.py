import base64

from typing import Dict

from src.main.api.configs.config import Config


class RequestSpecs:
    @staticmethod
    def _base_url() -> str:
        return f"{Config.get('server')}{Config.get('apiVersion')}"

    @staticmethod
    def default_req_headers() -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    @staticmethod
    def unauth_spec() -> Dict[str, str]:
        return RequestSpecs.default_req_headers()

    @staticmethod
    def admin_auth_spec():
        headers = RequestSpecs.default_req_headers()
        headers["Authorization"] = Config.get("ADMIN_AUTH_HEADER", "Basic YWRtaW46YWRtaW4=")
        return headers

    @staticmethod
    def auth_as_user(username, password):
        credentials = f"{username}:{password}".encode("utf-8")
        headers = RequestSpecs.default_req_headers()
        headers["Authorization"] = f"Basic {base64.b64encode(credentials).decode('ascii')}"
        return headers
