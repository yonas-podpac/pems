from pems.components.objects import UserProfile
from pems.helpers.database import db

class Authenticator:
    """Class for Handling Authentication Functionality"""
    def __init__(self):
        # Retrieve Authentication Lists from DB
        self.__roles = db.roles
        self.__user_profiles = db.user_profiles

    def is_valid_user(self, username: str) -> bool:
        check = False
        for user in self.__user_profiles:
            if user.username == username or user.email_address == username:
                check = True
                break
        return check

    def valid_roles(self) -> list[str]:
        """Function for retrieving values user roles"""
        return [role.role for role in self.__roles]
    
    def get_logged_in_user(self, username: str) -> UserProfile:
        """Function for getting the User Profile of the User currently Logged In"""
        try:
            return [user for user in self.__user_profiles if user.username == username][0]
        except Exception:
            return [user for user in self.__user_profiles if user.email_address == username][0]

    def get_user_by_email(self, email: str) -> UserProfile:
        """Function for getting the User Profile of the User Logged in with their Email"""
        return [user for user in self.__user_profiles if user.email_address == email][0]

    def role_to_string(self, role_id: str) -> str:
        """Function for getting the Role from it's UUID"""
        if role_id != "":
            return [role.role for role in self.__roles if role.id == role_id][0]
        return "viewer"
    
    def insert_user(self, entry: dict[str, str]) -> list[dict[str, any]]:
        """Function to Insert a New User to Supabase"""
        new_role = entry.pop("role")
        entry["role_id"] = [role.id for role in self.__roles if role.role == new_role][0]
        return db.insert("user_profiles", entry)

authenticator = Authenticator()