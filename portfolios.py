class OptionReplicatingPortfolio:
    def __init__(self, share_weight, bond_weight, stock_price):
        self.share_weight = share_weight
        self.bond_weight = bond_weight
        self.stock_price = stock_price

    def get_price(self):
        return (self.share_weight + self.bond_weight) * self.stock_price


class OptionExecutionPortfolio:
    def __init__(self, price, should_execute):
        self.price = price
        self.should_execute = should_execute

    def get_price(self):
        return self.price
