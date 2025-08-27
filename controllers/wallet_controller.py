from models.wallet import WalletModel

class WalletController:
    def __init__(self):
        self.model = WalletModel()

    def connect_wallet(self, address):
        self.model.add_wallet(address)
