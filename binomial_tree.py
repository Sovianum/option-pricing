from option import PriceInfo


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


class BinomialTree:
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
                    price_info_up = stock_price_tree[(curr_level + 1, parent_index * 2)]
                    price_info_down = stock_price_tree[(curr_level + 1, parent_index * 2 + 1)]

                    portfolio = calculate_replicating_portfolio(
                        self.option.get_payout(PriceInfo(
                            price_info_up.curr,
                            max_encountered=price_info_up.max_encountered
                        )),
                        self.option.get_payout(PriceInfo(
                            price_info_down.curr,
                            max_encountered=price_info_down.max_encountered
                        )),
                        stock_price_tree[(curr_level, parent_index)].curr,
                    )

                    replicating_portfolios[(curr_level, parent_index)] = portfolio
            else:
                do_calculate(curr_level + 1)

                for parent_index in range(2 ** curr_level):
                    portfolio_up, portfolio_down = replicating_portfolios[(curr_level + 1, parent_index * 2)], \
                                                   replicating_portfolios[(curr_level + 1, parent_index * 2 + 1)]

                    max_encountered_price = stock_price_tree[(curr_level, parent_index)].max_encountered

                    payout_up = self.option.get_payout(PriceInfo(
                        portfolio_up.get_price(),
                        max_encountered_price
                    ))

                    payout_down = self.option.get_payout(PriceInfo(
                        portfolio_down.get_price(),
                        max_encountered_price
                    ))

                    replicating_portfolios[(curr_level, parent_index)] = calculate_replicating_portfolio(
                        payout_up,
                        payout_down,
                        stock_price_tree[(curr_level, parent_index)].curr,
                    )

        do_calculate(0)

        return BinomialTree.PortfolioTree(replicating_portfolios, stock_price_tree, self.period_count)

    def calculate_replicating_portfolios_american(self):
        portfolio_tree = self.calculate_replicating_portfolios_european()
        up_probability = self._get_risk_neutral_probability()

        for period_index in reversed(range(portfolio_tree.get_period_count())):
            for node_index in range(portfolio_tree.get_node_count_at_period(period_index)):
                portfolio = portfolio_tree.get_portfolio(period_index, node_index)

                up_price, down_price = None, None
                if not portfolio_tree.has_children_portfolios(period_index, node_index):
                    price_info_up = portfolio_tree.get_stock_price_data(period_index + 1, node_index * 2)
                    price_info_down = portfolio_tree.get_stock_price_data(period_index + 1, node_index * 2 + 1)

                    up_price = self.option.get_payout(PriceInfo(
                        portfolio.stock_price * self.up_factor,
                        price_info_up.max_encountered
                    ))
                    down_price = self.option.get_payout(PriceInfo(
                        portfolio.stock_price * self.down_factor,
                        price_info_down.max_encountered
                    ))
                else:
                    portfolio_up, portfolio_down = portfolio_tree.get_children_portfolios(period_index, node_index)
                    up_price, down_price = portfolio_up.get_price(), portfolio_down.get_price()

                continuation_price = (up_price * up_probability + down_price * (1 - up_probability)) / (
                            1 + self.period_discount_rate)
                execution_price = self.option.get_payout(PriceInfo(
                    portfolio.stock_price,
                    portfolio_tree.get_stock_price_data(period_index, node_index).max_encountered
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

    def _get_risk_neutral_probability(self):
        return (1 + self.period_discount_rate - self.down_factor) / (self.up_factor - self.down_factor)

    def _get_stock_price_tree(self):
        result = {
            (0, 0): BinomialTree._PriceInfo(self.stock_price, self.stock_price)
        }
        for period_index in range(1, self.period_count + 1):
            for node_index in range(2 ** period_index):
                parent_id = (period_index - 1, node_index // 2)
                price_data = result[parent_id]
                price_factor = self.up_factor if node_index % 2 == 0 else self.down_factor
                result[(period_index, node_index)] = BinomialTree._PriceInfo(
                    price_data.curr * price_factor,
                    max(price_data.curr, price_data.max_encountered)
                )

        return result
