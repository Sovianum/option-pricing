from option import PriceInfo
from portfolios import OptionExecutionPortfolio
from utils import get_risk_neutral_probability


class BinomialTreeAmerican:
    def __init__(self, european_tree):
        self.european_tree = european_tree
        self.up_factor = european_tree.up_factor
        self.down_factor = european_tree.down_factor
        self.period_discount_rate = european_tree.period_discount_rate
        self.period_count = european_tree.period_count
        self.stock_price = european_tree.stock_price
        self.option = european_tree.option

    def calculate_replicating_portfolios(self):
        portfolio_tree = self.european_tree.calculate_replicating_portfolios()
        up_probability = get_risk_neutral_probability(self.period_discount_rate, self.up_factor, self.down_factor)

        for period_index in reversed(range(portfolio_tree.get_period_count())):
            for node_index in range(portfolio_tree.get_node_count_at_period(period_index)):
                portfolio = portfolio_tree.get_portfolio(period_index, node_index)

                up_price, down_price = self._get_price_pair(portfolio_tree, period_index, node_index)

                continuation_price = (up_price * up_probability + down_price * (1 - up_probability)) / (
                            1 + self.period_discount_rate)
                execution_price = self.option.get_payout(PriceInfo(
                    portfolio.stock_price,
                    portfolio_tree.get_stock_price_data(period_index, node_index).max_encountered,
                    is_terminal_state=True
                ))

                if execution_price > continuation_price:
                    portfolio_tree.update_portfolio(
                        period_index, node_index,
                        OptionExecutionPortfolio(execution_price, should_execute=True)
                    )
                else:
                    portfolio_tree.update_portfolio(
                        period_index, node_index,
                        OptionExecutionPortfolio(continuation_price, should_execute=False)
                    )

        return portfolio_tree

    def _get_price_pair(self, portfolio_tree, period_index, node_index):
        if not portfolio_tree.has_children_portfolios(period_index, node_index):
            return self._get_terminal_price_pair(portfolio_tree, period_index, node_index)
        else:
            return self._get_non_terminal_price_pair(portfolio_tree, period_index, node_index)

    def _get_terminal_price_pair(self, portfolio_tree, period_index, node_index):
        portfolio = portfolio_tree.get_portfolio(period_index, node_index)

        price_info_up = portfolio_tree.get_stock_price_data(period_index + 1, node_index * 2)
        price_info_down = portfolio_tree.get_stock_price_data(period_index + 1, node_index * 2 + 1)

        up_price = self.option.get_payout(PriceInfo(
            portfolio.stock_price * self.up_factor,
            price_info_up.max_encountered,
            is_terminal_state=True
        ))
        down_price = self.option.get_payout(PriceInfo(
            portfolio.stock_price * self.down_factor,
            price_info_down.max_encountered,
            is_terminal_state=True
        ))

        return up_price, down_price

    def _get_non_terminal_price_pair(self, portfolio_tree, period_index, node_index):
        portfolio_up, portfolio_down = portfolio_tree.get_children_portfolios(period_index, node_index)
        return portfolio_up.get_price(), portfolio_down.get_price()
