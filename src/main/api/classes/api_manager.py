from src.main.api.steps.admin_steps import AdminSteps
from src.main.api.steps.customer_management_steps import CustomerManagementSteps
from src.main.api.steps.manage_user_accounts_steps import ManageUserAccountsSteps
from src.main.api.steps.user_steps import UserSteps


class ApiManager:
    def __init__(self, created_objects: list):
        self.admin_steps = AdminSteps(created_objects)
        self.user_steps = UserSteps(created_objects)
        self.manage_user_accounts_steps = ManageUserAccountsSteps(created_objects)
        self.customer_management_steps = CustomerManagementSteps(created_objects)