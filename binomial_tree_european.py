from option import PriceInfo
from portfolio_tree import PortfolioTree
from portfolios import OptionReplicatingPortfolio
from utils import get_discount_factor


class BinomialTreeEuropean:
    class _PriceInfo:
        def __init__(self, curr, max_encountered):
            self.curr = curr
            self.max_encountered = max_encountered

    def __init__(self, up_factor, down_factor, period_discount_rate, period_count, stock_price, option):
        self.up_factor = up_factor
        self.down_factor = down_factor
        self.period_discount_rate = period_discount_rate
        self.period_count = period_count
        self.stock_price = stock_price
        self.option = option

    def calculate_replicating_portfolios(self):
        replicating_portfolios = {}
        stock_price_tree = self._get_stock_price_tree()

        def do_calculate(curr_level):
            if curr_level == self.period_count - 1:
                for parent_index in range(2 ** curr_level):
                    replicating_portfolios[(curr_level, parent_index)] = self._calculate_terminal_portfolio(
                        stock_price_tree, curr_level, parent_index
                    )
            else:
                do_calculate(curr_level + 1)

                for parent_index in range(2 ** curr_level):
                    replicating_portfolios[(curr_level, parent_index)] = self._calculate_non_terminal_portfolio(
                        replicating_portfolios, stock_price_tree, curr_level, parent_index
                    )

        do_calculate(0)

        return PortfolioTree(replicating_portfolios, stock_price_tree, self.period_count)

    def _calculate_terminal_portfolio(self, stock_price_tree, curr_level, parent_index):
        price_info_up = stock_price_tree[(curr_level + 1, parent_index * 2)]
        price_info_down = stock_price_tree[(curr_level + 1, parent_index * 2 + 1)]

        return self._calculate_replicating_portfolio(
            self.option.get_payout(PriceInfo(
                price_info_up.curr,
                max_encountered=price_info_up.max_encountered,
                is_terminal_state=True
            )),
            self.option.get_payout(PriceInfo(
                price_info_down.curr,
                max_encountered=price_info_down.max_encountered,
                is_terminal_state=True
            )),
            stock_price_tree[(curr_level, parent_index)].curr,
        )

    def _calculate_non_terminal_portfolio(self, replicating_portfolios, stock_price_tree, curr_level, parent_index):
        key_up = (curr_level + 1, parent_index * 2)
        key_down = (curr_level + 1, parent_index * 2 + 1)

        portfolio_up = replicating_portfolios[key_up]
        portfolio_down = replicating_portfolios[key_down]

        return self._calculate_replicating_portfolio(
            portfolio_up.get_price(),
            portfolio_down.get_price(),
            stock_price_tree[(curr_level, parent_index)].curr,
        )

    def _calculate_replicating_portfolio(self, payout_up, payout_down, stock_price):
        share_weight = (payout_up - payout_down) / (self.up_factor - self.down_factor) / stock_price
        bond_weight = (payout_up / stock_price - share_weight * self.up_factor) / (1 + self.period_discount_rate)
        return OptionReplicatingPortfolio(share_weight, bond_weight, stock_price)

    def _get_stock_price_tree(self):
        result = {
            (0, 0): BinomialTreeEuropean._PriceInfo(self.stock_price, self.stock_price)
        }
        for period_index in range(1, self.period_count + 1):
            for node_index in range(2 ** period_index):
                parent_id = (period_index - 1, node_index // 2)
                price_data = result[parent_id]
                price_factor = self.up_factor if node_index % 2 == 0 else self.down_factor
                curr_price = price_data.curr * price_factor
                result[(period_index, node_index)] = BinomialTreeEuropean._PriceInfo(
                    curr_price,
                    max(curr_price, price_data.max_encountered)
                )

        return result
