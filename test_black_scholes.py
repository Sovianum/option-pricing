import unittest

from binomial_tree_european import BinomialTreeEuropean
from option import Option
from crr import CRRBinomialTreeParameters
import black_scholes
from utils import get_discount_factor
import pandas as pd


class TestBinomialTree(unittest.TestCase):
    def test_black_scholes_to_binomial_tree_comparison(self):
        stock_price_volatility = 1
        time_horizon = 1
        period_counts = list(range(2, 15))

        stock_price = 1
        period_discount_rate = 0
        strike_price = 0.5

        def get_tree_price(period_count):
            crr_parameters = CRRBinomialTreeParameters(
                stock_price_volatility, time_horizon, period_count
            )

            tree = BinomialTreeEuropean(
                up_factor=crr_parameters.get_up_factor(),
                down_factor=crr_parameters.get_down_factor(),
                period_discount_rate=period_discount_rate,
                period_count=period_count,
                stock_price=stock_price,
                option=Option.long_call_option(strike_price),
                discount_rate_factor_gen=get_discount_factor,
            )

            portfolio_tree = tree.calculate_replicating_portfolios()
            return portfolio_tree.get_portfolio(0, 0).get_price()

        def get_black_scholes_price():
            black_and_scholes_option = black_scholes.Option()
            return black_and_scholes_option.get_call_price(black_scholes.Option.OptionParameters(
                stock_price, strike_price, period_discount_rate, stock_price_volatility, time_horizon
            ))

        print(pd.DataFrame({
            "periods": period_counts,
            "tree_price": [get_tree_price(period_count) for period_count in period_counts],
            "black_scholes_price": [get_black_scholes_price() for _ in period_counts]
        }))

        # for period_count in period_counts:
        #     print("periods: %d\ttree_price: %.5f\tblack_and_scholes_price: %.5f" % (
        #             period_count,
        #             get_tree_price(period_count),
        #             get_black_scholes_price()
        #         )
        #     )


if __name__ == '__main__':
    unittest.main()