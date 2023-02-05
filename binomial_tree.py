import numpy as np


class OptionReplicatingPortfolio:
    def __init__(self, share_weight, bond_weight, stock_price):
        self.share_weight = share_weight
        self.bond_weight = bond_weight
        self.stock_price = stock_price

    def get_norm_price(self):
        return self.share_weight + self.bond_weight

    def get_price(self):
        return self.get_norm_price() * self.stock_price


class BinomialTree:
    class PortfolioTree:
        def __init__(self, portfolio_map):
            self._portfolio_map = portfolio_map

        def get_root(self):
            return self.get_portfolio(0, 0)

        def get_portfolio(self, level, index):
            return self._portfolio_map[(level, index)]

    def __init__(self, up_factor, down_factor, period_discount_rate, period_count, stock_price, option):
        self.up_factor = up_factor
        self.down_factor = down_factor
        self.period_discount_rate = period_discount_rate
        self.period_count = period_count
        self.stock_price = stock_price
        self.option = option

    def calculate_replicating_portfolios(self):
        replicating_portfolios = {}
        relative_leaf_payouts = self._get_leaf_node_payouts() / self.stock_price

        def calculate_replicating_portfolio(rel_payout_up, rel_payout_down):
            share_weight = (rel_payout_up - rel_payout_down) / (self.up_factor - self.down_factor)
            bond_weight = (rel_payout_up - share_weight * self.up_factor) / (1 + self.period_discount_rate)
            return OptionReplicatingPortfolio(share_weight, bond_weight, self.stock_price)

        def do_calculate(curr_level):
            if curr_level == self.period_count - 1:
                for parent_index in range(2 ** curr_level):
                    portfolio = calculate_replicating_portfolio(
                        relative_leaf_payouts[parent_index * 2],
                        relative_leaf_payouts[parent_index * 2 + 1]
                    )

                    replicating_portfolios[(curr_level, parent_index)] = portfolio
            else:
                do_calculate(curr_level + 1)

                for parent_index in range(2 ** curr_level):
                    portfolio_up, portfolio_down = replicating_portfolios[(curr_level + 1, parent_index * 2)], \
                                                   replicating_portfolios[(curr_level + 1, parent_index * 2 + 1)]

                    price_up, price_down = portfolio_up.get_price(), portfolio_down.get_price()
                    payout_up, payout_down = self.option.get_payout(price_up), self.option.get_payout(price_down)

                    replicating_portfolios[(curr_level, parent_index)] = calculate_replicating_portfolio(
                        payout_up / self.stock_price,
                        payout_down / self.stock_price,
                    )

        do_calculate(0)

        return BinomialTree.PortfolioTree(replicating_portfolios)

    def _get_leaf_node_payouts(self):
        leaf_node_prices = self.stock_price * BinomialTree.get_leaf_node_price_factors(
            self.period_count, self.up_factor, self.down_factor
        )
        return np.array(list(map(self.option.get_payout, leaf_node_prices)))

    @staticmethod
    def get_leaf_node_price_factors(period_count, up_factor, down_factor):
        period_factors = []
        indices = np.array(range(2 ** period_count))

        for period_index in range(period_count):
            down_mask = (indices >> period_index) % 2

            period_factors.append(down_factor * down_mask + up_factor * (down_mask ^ 1))

        return np.prod(np.array([period_factors]), axis=1)[0]
