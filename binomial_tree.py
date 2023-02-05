import numpy as np


class OptionReplicatingPortfolio:
    def __init__(self, share_weight, bond_weight, stock_price):
        self.share_weight = share_weight
        self.bond_weight = bond_weight
        self.stock_price = stock_price

    def get_norm_price(self):
        return self.share_weight + self.bond_weight

    def get_price(self):
        return (self.share_weight + self.bond_weight) * self.stock_price


class BinomialTree:
    class PortfolioTree:
        def __init__(self, portfolio_map, period_count):
            self._portfolio_map = portfolio_map
            self.period_count = period_count

        def update_portfolio(self, level, index, portfolio):
            self._portfolio_map[(level, index)] = portfolio

        def get_root(self):
            return self.get_portfolio(0, 0)

        def get_portfolio(self, level, index):
            return self._portfolio_map[(level, index)]

        def get_children_portfolios(self, level, index):
            return self._portfolio_map[(level + 1, 2 * index)], self._portfolio_map[(level + 1, 2 * index + 1)]

        def has_children_portfolios(self, level, _):
            return level < self.period_count

        def get_period_count(self):
            return self.period_count

        def get_node_count_at_period(self, period):
            assert period < self.period_count
            return 2 ** period

    def __init__(self, up_factor, down_factor, period_discount_rate, period_count, stock_price, option):
        self.up_factor = up_factor
        self.down_factor = down_factor
        self.period_discount_rate = period_discount_rate
        self.period_count = period_count
        self.stock_price = stock_price
        self.option = option

    def calculate_replicating_portfolios_european(self):
        replicating_portfolios = {}
        stock_price_tree = self._get_stock_price_tree()

        def calculate_replicating_portfolio(payout_up, payout_down, stock_price):
            share_weight = (payout_up - payout_down) / (self.up_factor - self.down_factor) / stock_price
            bond_weight = (payout_up / stock_price - share_weight * self.up_factor) / (1 + self.period_discount_rate)
            return OptionReplicatingPortfolio(share_weight, bond_weight, stock_price)

        def do_calculate(curr_level):
            if curr_level == self.period_count - 1:
                for parent_index in range(2 ** curr_level):
                    portfolio = calculate_replicating_portfolio(
                        self.option.get_payout(stock_price_tree[(curr_level + 1, parent_index * 2)]),
                        self.option.get_payout(stock_price_tree[(curr_level + 1, parent_index * 2 + 1)]),
                        stock_price_tree[(curr_level, parent_index)],
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
                        payout_up,
                        payout_down,
                        stock_price_tree[(curr_level, parent_index)],
                    )

        do_calculate(0)

        return BinomialTree.PortfolioTree(replicating_portfolios, self.period_count)

    def calculate_replicating_portfolios_american(self):
        portfolio_tree = self.calculate_replicating_portfolios_european()
        up_probability = self._get_risk_neutral_probability()

        for period_index in range(portfolio_tree.get_period_count() - 1, -1, -1):
            for node_index in range(portfolio_tree.get_node_count_at_period(period_index)):
                portfolio = portfolio_tree.get_portfolio(period_index, node_index)

                up_price, down_price = None, None
                if not portfolio_tree.has_children_portfolios(period_index, node_index):
                    up_price = self.option.get_payout(portfolio.stock_price * self.up_factor)
                    down_price = self.option.get_payout(portfolio.stock_price * self.down_factor)
                else:
                    portfolio_up, portfolio_down = portfolio_tree.get_children_portfolios(period_index, node_index)
                    up_price, down_price = portfolio_up.get_price(), portfolio_down.get_price()

                continuation_price = (up_price * up_probability + down_price * (1 - up_probability)) / (1 + self.period_discount_rate)
                execution_price = self.option.get_payout(portfolio.stock_price)

                # if execution_price > continuation_price:


    def _get_risk_neutral_probability(self):
        return (1 + self.period_discount_rate - self.down_factor) / (self.up_factor - self.down_factor)

    def _get_stock_price_tree(self):
        result = {
            (0, 0): self.stock_price
        }
        for period_index in range(1, self.period_count + 1):
            for node_index in range(2**period_index):
                parent_id = (period_index - 1, node_index // 2)
                parent_price = result[parent_id]
                price_factor = self.up_factor if node_index % 2 == 0 else self.down_factor
                result[(period_index, node_index)] = parent_price * price_factor

        return result
