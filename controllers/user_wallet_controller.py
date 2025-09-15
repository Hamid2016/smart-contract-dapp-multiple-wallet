from models.user_wallet import UserWalletModel  # Updated import path

class UserWalletController:
    def __init__(self):
        self.model = UserWalletModel()

    def assign_wallet_to_user(self, user_id, wallet_id, date=None, userwallet=None):
        self.model.link_user_wallet(user_id, wallet_id, date, userwallet)

    def get_user_wallets(self, user_id):
        return self.model.get_wallets_for_user(user_id)

    def close_connection(self):
        self.model.close()
