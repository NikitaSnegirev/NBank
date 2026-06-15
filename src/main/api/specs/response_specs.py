from enum import Enum
from http import HTTPStatus
from typing import Callable

from requests import Response


class ResponseError(str, Enum):
    MAX_TRANSFER_AMOUNT = "Transfer amount cannot exceed 10000"
    MIN_TRANSFER_AMOUNT = "Invalid transfer: insufficient funds or invalid accounts"
    INVALID_TRANSFER = "Invalid transfer: insufficient funds or invalid accounts"
    UNAUTHORIZED_ACCESS_TO_ACCOUNT = "Unauthorized access to account"
    NAME = "Name must contain two words with letters only"
    DEPOSIT_OVER_LIMIT = "Deposit amount exceeds the 5000 limit"
    MIN_DEPOSIT_AMOUNT = "Invalid account or amount"
    USERNAME_CANNOT_BE_BLANK = "Username cannot be blank"
    USERNAME_MUST_BY_BETWEEN_3_AND_5_CHARACTERS = "Username must be between 3 and 15 characters"
    USERNAME_MUST_CONTAIN_ONLY_ALLOWED_SYMBOLS = "Username must contain only letters, digits, dashes, underscores, and dots"


class ResponseSpecs:
    @staticmethod
    def _make_status_checker(expected_statuses: list[HTTPStatus]) -> Callable[[Response], None]:
        def check(response: Response):
            assert response.status_code in expected_statuses, (
                f"Expected status {expected_statuses}, but got {response.status_code}. "
                f"Response body: {response.text}"
            )
        return check

    @staticmethod
    def request_returns_ok() -> Callable[[Response], None]:
        return ResponseSpecs._make_status_checker([HTTPStatus.OK])

    @staticmethod
    def entity_was_created() -> Callable[[Response], None]:
        return ResponseSpecs._make_status_checker([HTTPStatus.CREATED])

    @staticmethod
    def entity_was_deleted() -> Callable[[Response], None]:
        return ResponseSpecs._make_status_checker([HTTPStatus.OK, HTTPStatus.NO_CONTENT])

    @staticmethod
    def request_returns_bad_request(
        error_key: str,
        error_value: str
    ) -> Callable[[Response], None]:
        def check(response: Response):
            assert response.status_code == HTTPStatus.BAD_REQUEST, (
                f"Expected 400 BAD_REQUEST, got {response.status_code}. Response: {response.text}"
            )
            actual_value = response.json().get(error_key)
            assert error_value in actual_value, (
                f"Expected error field '{error_key}' to be '{error_value}', but got '{actual_value}'."
            )
        return check

    @staticmethod
    def request_returns_bad_request_with_text(
            error_text: ResponseError
    ) -> Callable[[Response], None]:
        def check(response: Response):
            expected_statuses = [HTTPStatus.BAD_REQUEST, HTTPStatus.FORBIDDEN]
            assert response.status_code in expected_statuses, (
                f"Expected status {expected_statuses}, got {response.status_code}. Response: {response.text}"
            )
            assert error_text.value in response.text, (
                f"Expected response text to contain '{error_text.value}', but got '{response.text}'."
            )
        return check

    @staticmethod
    def profile_updated_successfully():
        def check(response: Response):
            check_ok = ResponseSpecs.request_returns_ok()
            check_ok(response)

            actual_message = response.json().get("message")
            assert actual_message == "Profile updated successfully", (
                f"Expected message 'Profile updated successfully', but got '{actual_message}'."
            )

        return check

    @staticmethod
    def transfer_successfully():
        def check(response: Response):
            check_ok = ResponseSpecs.request_returns_ok()
            check_ok(response)

            actual_message = response.json().get("message")
            assert actual_message == "Transfer successful", (
                f"Expected message 'Transfer successful', but got '{actual_message}'."
            )

        return check
