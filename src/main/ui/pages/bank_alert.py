from enum import Enum


class BankAlert(str, Enum):
    USER_CREATED_SUCCESSFULLY = "✅ User created successfully!"
    USERNAME_MUST_BE_BETWEEN_3_AND_15_CHARACTERS = "Username must be between 3 and 15 characters"
    NEW_ACCOUNT_CREATED = "✅ New Account Created! Account Number: "

    INVALID_AMOUNT_DEPOSIT = "❌ Please enter a valid amount."
    AMOUNT_MORE_THAN_5000_DEPOSIT = "❌ Please deposit less or equal to 5000$."
    ACCOUNT_NOT_SELECTED_DEPOSIT = "❌ Please select an account."

    MIN_AMOUNT_TRANSFER = "❌ Error: Transfer amount must be at least 0.01"
    MAX_AMOUNT_TRANSFER = "❌ Error: Transfer amount cannot exceed 10000"
    INSUFFICIENT_FUNDS_OR_INVALID_ACCOUNTS_TRANSFER = "❌ Error: Invalid transfer: insufficient funds or invalid accounts"
    FILL_ALL_FIELDS_TRANSFER = "❌ Please fill all fields and confirm."

    UPDATED_SUCCESSFULLY_NAME = "✅ Name updated successfully!"
    UPDATED_UNSUCCESSFULLY_NAME = "Name must contain two words with letters only"

def successfully_deposited(amount: str, account_number: str) -> str:
    return f"✅ Successfully deposited ${amount} to account {account_number}!"

def successfully_transferred(amount: str, account_number: str) -> str:
    return f"✅ Successfully transferred ${amount} to account {account_number}!"