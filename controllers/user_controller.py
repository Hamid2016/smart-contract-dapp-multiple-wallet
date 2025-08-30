from models.user import UserModel

class UserController:
    def __init__(self):
        self.model = UserModel()

    def register(self, username, password, email, phone_number, country, ip_address, browser, os):
        success = self.model.create_user(username, password, email, phone_number, country, ip_address, browser, os)
        if success:
            return {"success": True, "message": "User registered successfully"}
        return {"success": False, "message": "Username already exists"}

    def login(self, username, password):
        user = self.model.validate_user(username, password)
        if user:
            self.model.update_login_time(username)
            return {"success": True, "message": "Login successful"}
        return {"success": False, "message": "Invalid credentials"}

    def logout(self, username):
        self.model.update_logout_time(username)
        return {"success": True, "message": "Logout recorded"}

    def get_user_info(self, username):
        return self.model.get_user(username)
