from models.policy import PolicyModel

class PolicyController:
    def __init__(self):
        self.model = PolicyModel()

    def create_policy(self, address, name, premium, coverage):
        self.model.save_policy(address, name, premium, coverage)
