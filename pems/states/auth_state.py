import reflex as rx
from pems.helpers.database import db
from pems.helpers.authenticator import authenticator
import re
import time
from pems.states.user_state import UserState
from pems.components.objects import UserProfile

class AuthState(UserState):
    """State for tracking changes to PEMS"""
    # logged_in: bool = False
    username: str = ""
    email: str = ""
    password: str = ""
    confirm_password: str = ""
    first_name: str = ""
    last_name: str = ""
    role: str = ""
    roles: list[str] = authenticator.valid_roles()
    last_activity_time: float = 0.0
    TIMEOUT: int = 30 * 60
    MIN_LENGTH: int = 11
    is_login_form_open: bool = False
    is_signup_form_open: bool = False
    error_message: str = ""
    
    @rx.var
    def is_valid_email(self) -> bool:
        """Variable Checking for valid Podpac Email"""
        return "@podpac.com.au" in self.email

    @rx.var
    def has_min_length(self) -> bool:
        """Variable Checking for Minimum Length in Password"""
        return len(self.password) >= self.MIN_LENGTH
    
    @rx.var
    def has_lowercase(self) -> bool:
        """Variable Checking for Lowercase in Password"""
        return bool(re.search(r"[a-z]", self.password))

    @rx.var
    def has_uppercase(self) -> bool:
        """Variable Checking for Uppercase in Password"""
        return bool(re.search(r"[A-Z]", self.password))
    
    @rx.var
    def has_number(self) -> bool:
        """Variable Checking for Number in Password"""
        return bool(re.search(r"\d", self.password))

    @rx.var
    def has_special(self) -> bool:
        """Variable Checking for Special Character in Password"""
        return bool(re.search(r"[!@#$%^&*()_\-=\[\]{};:|<>,./?~`]", self.password))

    @rx.var
    def passwords_match(self) -> bool:
        """Variable Checking that Passwords Match"""
        if not self.confirm_password:
            return False
        return self.password == self.confirm_password
    
    @rx.var
    def valid_password(self) -> bool:
        """Variable Checking that Password Parameters are Valid"""
        return (
            self.has_min_length and
            self.has_lowercase and
            self.has_uppercase and
            self.has_number and
            self.has_special and
            self.passwords_match
        )
    
    @rx.var
    def valid_signup(self) -> bool:
        """Variable Checking that Sign Up Parameters are Valid"""
        return (
            self.is_valid_email and
            self.valid_password
        )
    
    # --- Form Functions ---
    def load(self):
        self.is_login_form_open = False
        self.is_signup_form_open = False
        self.error_message = ""
        logged_in_email = db.check_active_session()
        if logged_in_email != "":
            self.logged_in = True
            self.user = authenticator.get_user_by_email(logged_in_email)
        self.register_activity()

    def update_username(self, value: str):
        """Function for Updating the Username"""
        self.username = value

    def update_email(self, value: str):
        """Function for Updating the Email Address"""
        self.email = value

    def update_first_name(self, value: str):
        """Function for Updating the First Name"""
        self.first_name = value
    
    def update_last_name(self, value: str):
        """"Function for Updating the Last Name"""
        self.last_name = value

    def update_password(self, value: str):
        """Function for Updating the Password"""
        self.password = value

    def update_confirm_password(self, value: str):
        """Function for Updating the Confirm Password"""
        self.confirm_password = value
        
    def update_role(self, value: str):
        """Function for Updating the Role"""
        self.role = value

    def toggle_login_form(self):
        """Function for opening or closing the login form"""
        self.is_login_form_open = not self.is_login_form_open

    def toggle_signup_form(self):
        """Function for opening or closing the new login form"""
        self.is_signup_form_open = not self.is_signup_form_open
        self.is_login_form_open =  not self.is_signup_form_open

    def login(self, link: str):
        """Function for logging into PEMS"""
        # db.login("yona.sandt", "PodpacTech1234!")
        self.error_message = ""
        self.logged_in = db.login(self.username, self.password)
        print(self.logged_in)
        if self.logged_in:
            self.last_activity_time = time.time()
            self.user = authenticator.get_logged_in_user(self.username)
            self.password = ""
            self.is_login_form_open = False
            return rx.redirect(link)
        else:
            self.error_message = "Login Credentials were incorrect."
    
    def logout(self, link: str):
        """Function for logging out of PEMS"""
        if db.logout():
            self.logged_in = False
            self.last_activity_time = 0
            self.user = self.default_user()
            self.username = ""
            return rx.redirect(link)

    def inactive_logout(self):
        """Function for logging out of PEMS due to inactivity"""
        self.logout("/") # default logout to index
        return rx.window_alert("You have been logged out due to 15 minutes of inactivity.")
    
    def register_activity(self):
        """Resets timer when the user interacts with PEMS"""
        if not self.logged_in:
            return
        
        current_time = time.time()

        # Check if timeout has been reached
        if current_time - self.last_activity_time > self.TIMEOUT:
            return self.inactive_logout()
        
        # Otherwise update last active time
        self.last_activity_time = current_time

    def signup(self):
        """Function for signing up to PEMS"""
        self.error_message = ""
        if not self.valid_signup:
            self.error_message = "Please satisfy all password and email requirements first"
            print(f"[ERROR] Sign up parameters are invalid")
            return

        if db.signup(email=self.email, password=self.email):
            authenticator.insert_user({
                "username": self.username,
                "email_address": self.email,
                "name": self.first_name + " " + self.last_name,
                "role": self.role
            })
            self.email = ""
            self.username = ""
            self.first_name = ""
            self.last_name = ""
            self.password = ""
            self.confirm_password = ""
            self.is_signup_form_open = False
            self.is_login_form_open = True
        else:
            self.error_message = "An error has occurred while attempting to sign you up. Please try again later."
            
    def reset_password(self):
        """Function for Resetting Password"""
        if authenticator.is_valid_user(self.username):
            db.request_reset_password(self.username)
        else:
            self.error_message = "Please enter a valid username or email address"
    
    def handle_reset_password(self):
        """Function for Handling Resetting Password"""
        self.error_message = ""
        if not self.valid_password:
            self.error_message = "Please satisfy all password and email requirements first"
            print(f"[ERROR] Password parameters are invalid")
            return
        
        if db.reset_password(self.username, self.password):
            self.password = ""
            self.confirm_password = ""
            self.is_signup_form_open = False
            self.is_login_form_open = True
        else:
            self.error_message = "An error has occurred while attempting to reset your password"


