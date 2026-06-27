import random

import allure
import pytest

from src.main.api.assertions.account_assertions import AccountAssertions
from src.main.api.classes.api_manager import ApiManager
from src.main.api.fixtures.prepare_data_fixtures import PreparedUserAccount
from src.main.api.models.comparison.model_assertions import ModelAssertions
from src.main.api.models.transfer_request import TransferRequest
from src.main.api.models.transfer_response import TransferResponse
from src.main.api.specs.response_specs import ResponseError


FRAUD_APPROVED_MOCK = {
    "status": "SUCCESS",
    "decision": "APPROVED",
    "riskScore": 0.2,
    "reason": "Low risk transaction",
    "requiresManualReview": False,
    "additionalVerificationRequired": False,
}

FRAUD_APPROVED_EXPECTED = {
    "fraudRiskScore": FRAUD_APPROVED_MOCK["riskScore"],
    "fraudReason": FRAUD_APPROVED_MOCK["reason"],
    "requiresManualReview": False,
    "requiresVerification": False,
}

FRAUD_MANUAL_REVIEW_MOCK = {
    "status": "SUCCESS",
    "decision": "APPROVED",
    "riskScore": 0.75,
    "reason": "Suspicious transaction requires manual review",
    "requiresManualReview": True,
    "additionalVerificationRequired": False,
}

FRAUD_MANUAL_REVIEW_EXPECTED = {
    "fraudRiskScore": FRAUD_MANUAL_REVIEW_MOCK["riskScore"],
    "fraudReason": FRAUD_MANUAL_REVIEW_MOCK["reason"],
    "requiresManualReview": True,
    "requiresVerification": False,
}

FRAUD_VERIFICATION_REQUIRED_MOCK = {
    "status": "SUCCESS",
    "decision": "APPROVED",
    "riskScore": 0.6,
    "reason": "Additional verification required",
    "requiresManualReview": False,
    "additionalVerificationRequired": True,
}

FRAUD_VERIFICATION_REQUIRED_EXPECTED = {
    "fraudRiskScore": FRAUD_VERIFICATION_REQUIRED_MOCK["riskScore"],
    "fraudReason": FRAUD_VERIFICATION_REQUIRED_MOCK["reason"],
    "requiresManualReview": False,
    "requiresVerification": True,
}

FRAUD_REJECTED_MOCK = {
    "status": "SUCCESS",
    "decision": "REJECTED",
    "riskScore": 0.95,
    "reason": "High risk transaction",
    "requiresManualReview": False,
    "additionalVerificationRequired": False,
}

FRAUD_REJECTED_EXPECTED = {
    "fraudRiskScore": FRAUD_REJECTED_MOCK["riskScore"],
    "fraudReason": FRAUD_REJECTED_MOCK["reason"],
    "requiresManualReview": False,
    "requiresVerification": False,
}

TRANSFER_APPROVED_EXPECTED = {
    "status": "APPROVED",
    "message": "Transfer approved and processed immediately",
    **FRAUD_APPROVED_EXPECTED,
}

TRANSFER_MANUAL_REVIEW_EXPECTED = {
    "status": "MANUAL_REVIEW_REQUIRED",
    "message": "Transfer requires manual review",
    **FRAUD_MANUAL_REVIEW_EXPECTED,
}

TRANSFER_VERIFICATION_REQUIRED_EXPECTED = {
    "status": "APPROVED",
    "message": "Transfer approved and processed immediately",
    **FRAUD_VERIFICATION_REQUIRED_EXPECTED,
}

TRANSFER_REJECTED_EXPECTED = {
    "status": "MANUAL_REVIEW_REQUIRED",
    "message": "Transfer requires manual review",
    **FRAUD_REJECTED_EXPECTED,
}


@pytest.mark.api
@pytest.mark.api_version("with_fraud_check")
@pytest.mark.prepare_users(number=2)
@pytest.mark.prepare_accounts(number=2, deposit=5000)
class TestTransferWithFraudCheck:
    @pytest.mark.fraud_check_mock(
        port=8080,
        endpoint=r"/.*",
        **FRAUD_APPROVED_MOCK,
    )
    def test_transfer_with_fraud_check(
        self,
        api_manager: ApiManager,
        prepared_user_accounts: list[PreparedUserAccount],
        fraud_check_mock_server,
    ):
        with allure.step("Prepare sender/receiver accounts (2 accounts with deposit=5000)"):
            sender = prepared_user_accounts[0]
            receiver = prepared_user_accounts[1]
            sender_balance_before = AccountAssertions.get_balance(api_manager, sender.account.accountNumber)
            receiver_balance_before = AccountAssertions.get_balance(api_manager, receiver.account.accountNumber)

        with allure.step("Transfer with fraud check"):
            transfer_amount = round(random.uniform(0.1, 4999.9), 2)
            transfer_request = TransferRequest(
                senderAccountId=sender.account.id,
                receiverAccountId=receiver.account.id,
                amount=transfer_amount,
            )
            transfer_response = api_manager.user_steps.transfer_with_fraud_check(
                sender.user,
                transfer_request,
            )

        with allure.step("Validate transfer response matches mocked fraud decision"):
            expected = TransferResponse(
                amount=transfer_amount,
                senderAccountId=sender.account.id,
                receiverAccountId=receiver.account.id,
                **TRANSFER_APPROVED_EXPECTED,
            )
            ModelAssertions(expected, transfer_response).match()

        with allure.step("Validate approved transfer changes account balances"):
            AccountAssertions.balances_changed_by_transfer(
                api_manager,
                sender.account.accountNumber,
                receiver.account.accountNumber,
                sender_balance_before,
                receiver_balance_before,
                transfer_amount,
            )

    @pytest.mark.fraud_check_mock(
        port=8080,
        endpoint=r"/.*",
        **FRAUD_VERIFICATION_REQUIRED_MOCK,
    )
    def test_transfer_with_fraud_check_verification_required(
        self,
        api_manager: ApiManager,
        prepared_user_accounts: list[PreparedUserAccount],
        fraud_check_mock_server,
    ):
        with allure.step("Prepare sender/receiver accounts (2 accounts with deposit=5000)"):
            sender = prepared_user_accounts[0]
            receiver = prepared_user_accounts[1]
            sender_balance_before = AccountAssertions.get_balance(api_manager, sender.account.accountNumber)
            receiver_balance_before = AccountAssertions.get_balance(api_manager, receiver.account.accountNumber)

        with allure.step("Transfer with fraud check that requires additional verification"):
            transfer_amount = round(random.uniform(0.1, 4999.9), 2)
            transfer_request = TransferRequest(
                senderAccountId=sender.account.id,
                receiverAccountId=receiver.account.id,
                amount=transfer_amount,
            )
            transfer_response = api_manager.user_steps.transfer_with_fraud_check(
                sender.user,
                transfer_request,
            )

        with allure.step("Validate transfer response matches mocked verification decision"):
            expected = TransferResponse(
                amount=transfer_amount,
                senderAccountId=sender.account.id,
                receiverAccountId=receiver.account.id,
                **TRANSFER_VERIFICATION_REQUIRED_EXPECTED,
            )
            ModelAssertions(expected, transfer_response).match()

        with allure.step("Validate approved transfer with verification flag changes account balances"):
            AccountAssertions.balances_changed_by_transfer(
                api_manager,
                sender.account.accountNumber,
                receiver.account.accountNumber,
                sender_balance_before,
                receiver_balance_before,
                transfer_amount,
            )

    @pytest.mark.fraud_check_mock(
        port=8080,
        endpoint=r"/.*",
        **FRAUD_REJECTED_MOCK,
    )
    def test_transfer_with_fraud_check_rejected_decision_requires_manual_review(
        self,
        api_manager: ApiManager,
        prepared_user_accounts: list[PreparedUserAccount],
        fraud_check_mock_server,
    ):
        with allure.step("Prepare sender/receiver accounts (2 accounts with deposit=5000)"):
            sender = prepared_user_accounts[0]
            receiver = prepared_user_accounts[1]
            sender_balance_before = AccountAssertions.get_balance(api_manager, sender.account.accountNumber)
            receiver_balance_before = AccountAssertions.get_balance(api_manager, receiver.account.accountNumber)

        with allure.step("Transfer with fraud check that rejects high risk transaction"):
            transfer_amount = round(random.uniform(0.1, 4999.9), 2)
            transfer_request = TransferRequest(
                senderAccountId=sender.account.id,
                receiverAccountId=receiver.account.id,
                amount=transfer_amount,
            )
            transfer_response = api_manager.user_steps.transfer_with_fraud_check(
                sender.user,
                transfer_request,
            )

        with allure.step("Validate transfer response matches mocked rejection decision"):
            expected = TransferResponse(
                amount=transfer_amount,
                senderAccountId=sender.account.id,
                receiverAccountId=receiver.account.id,
                **TRANSFER_REJECTED_EXPECTED,
            )
            ModelAssertions(expected, transfer_response).match()

        with allure.step("Validate rejected fraud decision does not change account balances"):
            AccountAssertions.balances_unchanged(
                api_manager,
                sender.account.accountNumber,
                receiver.account.accountNumber,
                sender_balance_before,
                receiver_balance_before,
            )

    @pytest.mark.fraud_check_mock(
        port=8080,
        endpoint=r"/.*",
        **FRAUD_MANUAL_REVIEW_MOCK,
    )
    def test_transfer_with_fraud_check_manual_review(
        self,
        api_manager: ApiManager,
        prepared_user_accounts: list[PreparedUserAccount],
        fraud_check_mock_server,
    ):
        with allure.step("Prepare sender/receiver accounts (2 accounts with deposit=5000)"):
            sender = prepared_user_accounts[0]
            receiver = prepared_user_accounts[1]
            sender_balance_before = AccountAssertions.get_balance(api_manager, sender.account.accountNumber)
            receiver_balance_before = AccountAssertions.get_balance(api_manager, receiver.account.accountNumber)

        with allure.step("Transfer with fraud check that requires manual review"):
            transfer_amount = round(random.uniform(0.1, 4999.9), 2)
            transfer_request = TransferRequest(
                senderAccountId=sender.account.id,
                receiverAccountId=receiver.account.id,
                amount=transfer_amount,
            )
            transfer_response = api_manager.user_steps.transfer_with_fraud_check(
                sender.user,
                transfer_request,
            )

        with allure.step("Validate transfer response matches mocked manual review decision"):
            expected = TransferResponse(
                amount=transfer_amount,
                senderAccountId=sender.account.id,
                receiverAccountId=receiver.account.id,
                **TRANSFER_MANUAL_REVIEW_EXPECTED,
            )
            ModelAssertions(expected, transfer_response).match()

        with allure.step("Validate manual review transfer does not change account balances"):
            AccountAssertions.balances_unchanged(
                api_manager,
                sender.account.accountNumber,
                receiver.account.accountNumber,
                sender_balance_before,
                receiver_balance_before,
            )

    @pytest.mark.fraud_check_mock(
        port=8080,
        endpoint=r"/.*",
        **FRAUD_APPROVED_MOCK,
    )
    @pytest.mark.parametrize(
        "transfer_amount, error_text",
        [
            (0, ResponseError.INVALID_ACCOUNTS_OR_AMOUNT),
            (-0.01, ResponseError.INVALID_ACCOUNTS_OR_AMOUNT),
            (10000.1, ResponseError.MAX_TRANSFER_AMOUNT),
        ],
    )
    def test_transfer_with_fraud_check_invalid_amount(
        self,
        api_manager: ApiManager,
        prepared_user_accounts: list[PreparedUserAccount],
        fraud_check_mock_server,
        transfer_amount: float,
        error_text: ResponseError,
    ):
        with allure.step("Prepare sender/receiver accounts (2 accounts with deposit=5000)"):
            sender = prepared_user_accounts[0]
            receiver = prepared_user_accounts[1]
            sender_balance_before = AccountAssertions.get_balance(api_manager, sender.account.accountNumber)
            receiver_balance_before = AccountAssertions.get_balance(api_manager, receiver.account.accountNumber)

        with allure.step("Try transfer with fraud check using invalid amount"):
            transfer_request = TransferRequest(
                senderAccountId=sender.account.id,
                receiverAccountId=receiver.account.id,
                amount=transfer_amount,
            )
            api_manager.user_steps.transfer_with_fraud_check_invalid_data(
                sender.user,
                transfer_request,
                error_text,
            )

        with allure.step("Validate invalid amount does not change account balances"):
            AccountAssertions.balances_unchanged(
                api_manager,
                sender.account.accountNumber,
                receiver.account.accountNumber,
                sender_balance_before,
                receiver_balance_before,
            )

    @pytest.mark.fraud_check_mock(
        port=8080,
        endpoint=r"/.*",
        **FRAUD_APPROVED_MOCK,
    )
    def test_transfer_with_fraud_check_insufficient_funds(
        self,
        api_manager: ApiManager,
        prepared_user_accounts: list[PreparedUserAccount],
        fraud_check_mock_server,
    ):
        with allure.step("Prepare sender/receiver accounts (2 accounts with deposit=5000)"):
            sender = prepared_user_accounts[0]
            receiver = prepared_user_accounts[1]
            sender_balance_before = AccountAssertions.get_balance(api_manager, sender.account.accountNumber)
            receiver_balance_before = AccountAssertions.get_balance(api_manager, receiver.account.accountNumber)

        with allure.step("Try transfer with fraud check when sender has insufficient funds"):
            transfer_request = TransferRequest(
                senderAccountId=sender.account.id,
                receiverAccountId=receiver.account.id,
                amount=float(sender_balance_before) + 0.01,
            )
            api_manager.user_steps.transfer_with_fraud_check_invalid_data(
                sender.user,
                transfer_request,
                ResponseError.INSUFFICIENT_FUNDS,
            )

        with allure.step("Validate insufficient funds does not change account balances"):
            AccountAssertions.balances_unchanged(
                api_manager,
                sender.account.accountNumber,
                receiver.account.accountNumber,
                sender_balance_before,
                receiver_balance_before,
            )

    @pytest.mark.fraud_check_mock(
        port=8080,
        endpoint=r"/.*",
        **FRAUD_APPROVED_MOCK,
    )
    def test_transfer_with_fraud_check_user_has_no_access_to_other_user_account(
        self,
        api_manager: ApiManager,
        prepared_user_accounts: list[PreparedUserAccount],
        fraud_check_mock_server,
    ):
        with allure.step("Prepare accounts owned by different users"):
            sender = prepared_user_accounts[0]
            receiver = prepared_user_accounts[1]
            sender_balance_before = AccountAssertions.get_balance(api_manager, sender.account.accountNumber)
            receiver_balance_before = AccountAssertions.get_balance(api_manager, receiver.account.accountNumber)

        with allure.step("Try transfer while authenticated as a user who does not own sender account"):
            transfer_request = TransferRequest(
                senderAccountId=sender.account.id,
                receiverAccountId=receiver.account.id,
                amount=100,
            )
            api_manager.user_steps.transfer_with_fraud_check_invalid_data(
                receiver.user,
                transfer_request,
                ResponseError.UNAUTHORIZED_ACCESS_TO_ACCOUNT,
            )

        with allure.step("Validate unauthorized transfer does not change account balances"):
            AccountAssertions.balances_unchanged(
                api_manager,
                sender.account.accountNumber,
                receiver.account.accountNumber,
                sender_balance_before,
                receiver_balance_before,
            )
