# user_controller.py

from models.user import UserModel

class UserController:
    def __init__(self):
        # Initialize the UserModel to access database operations
        self.model = UserModel()

    def register_user(self, username, password):
        """
        Creates a new user with a hashed password.
        Returns True if successful, False if username already exists.
        """
        return self.model.create_user(username, password)

    def login_user(self, username, password):
        """
        Validates user credentials.
        If valid, updates last_login and returns user data.
        If invalid, returns None.
        """
        user = self.model.validate_user(username, password)
        if user:
            self.model.update_login_time(username)
            return user
        return None

    def logout_user(self, username):
        """
        Updates last_logout timestamp.
        You can call this when the user logs out.
        """
        self.model.update_logout_time(username)
        return True

    def get_user(self, username):
        """
        Retrieves user data by username.
        Returns a dictionary with user info or None.
        """
        return self.model.get_user(username)

    def close(self):
        """
        Closes the database connection.
        """
        self.model.close()
