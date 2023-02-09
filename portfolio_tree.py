class PortfolioTree:
    def __init__(self, portfolio_map, stock_price_map, period_count):
        self._portfolio_map = portfolio_map
        self._stock_price_map = stock_price_map
        self.period_count = period_count

    def get_stock_price_data(self, level, index):
        return self._stock_price_map[(level, index)]

    def update_portfolio(self, level, index, portfolio):
        self._portfolio_map[(level, index)] = portfolio

    def get_root_portfolio(self):
        return self.get_portfolio(0, 0)

    def get_portfolio(self, level, index):
        return self._portfolio_map[(level, index)]

    def get_children_portfolios(self, level, index):
        return self._portfolio_map[(level + 1, 2 * index)], self._portfolio_map[(level + 1, 2 * index + 1)]

    def has_children_portfolios(self, level, _):
        return level < self.period_count - 1

    def get_period_count(self):
        return self.period_count

    def get_node_count_at_period(self, period):
        assert period < self.period_count
        return 2 ** period
