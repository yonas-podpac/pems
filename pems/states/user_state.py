import reflex as rx
from pems.components.objects import UserProfile
from pems.helpers.authenticator import authenticator

class UserState(rx.State):
    logged_in: bool = False
    user: UserProfile = None

    @rx.var
    def get_user_name(self) -> str:
        """Variable of User's Full Name"""
        if self.__check_login():
            return self.user.name
        return ""

    @rx.var
    def is_admin(self) -> bool:
        """Variable Checking if Current role is Admin"""
        return self.__generic_role_check("admin")

    @rx.var
    def is_technician(self) -> bool:
        """Variable Checking if Current role is Technician"""
        return self.__generic_role_check("technician")

    @rx.var
    def is_operator(self) -> bool:
        """Variable Checking if Current role is Operator"""
        return self.__generic_role_check("operator")
    
    @rx.var
    def is_viewer(self) -> bool:
        """Variable Checking if Current role is Viewer"""
        return self.__generic_role_check("viewer")
    
    def default_user(self) -> UserProfile:
        return UserProfile("", "", "", "", "")

    # -- Helper Functions ---
    def __check_login(self) -> bool:
        """Function to check if Logged In"""
        if not self.logged_in:
            return False
        elif self.user is None:
            self.logged_in = False
            self.user = self.default_user()
            return False
        return True

    def __generic_role_check(self, role: str) -> bool:
        """Generic Function to Check if Role matches Desired Role"""
        # Return False if no user is logged in
        if not self.__check_login():
            return False
        # Otherwise check user's role
        return authenticator.role_to_string(self.user.role_id) == role