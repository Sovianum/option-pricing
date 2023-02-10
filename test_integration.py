import unittest

from binomial_tree_european import BinomialTreeEuropean
from binomial_tree_american import BinomialTreeAmerican
from option import Option
from crr import CRRBinomialTreeParameters
from utils import get_discount_rate, get_discount_factor


class TestIntegration(unittest.TestCase):
    def test_vanilla_option(self):
        for period_count in [3, 8]:
            with self.subTest(period_count):
                total_length = 5
                stock_price = 100
                strike_price = 100
                annual_discount_rate = 0.05
                discount_rate = get_discount_rate(
                    continuous_interest_rate=annual_discount_rate, period_length=total_length / period_count
                )

                crr_parameters = CRRBinomialTreeParameters(
                    stock_price_volatility=0.2, time_horizon=total_length, period_count=period_count
                )
                up_factor, down_factor = crr_parameters.get_up_factor(), crr_parameters.get_down_factor()

                call_binomial_tree = BinomialTreeEuropean(
                    up_factor=up_factor, down_factor=down_factor, period_discount_rate=discount_rate,
                    period_count=period_count, stock_price=stock_price, option=Option.long_call_option(strike_price),
                )
                call_portfolio_tree = call_binomial_tree.calculate_replicating_portfolios()
                call_price = call_portfolio_tree.get_root_portfolio().get_price()

                put_binomial_tree = BinomialTreeEuropean(
                    up_factor=up_factor, down_factor=down_factor, period_discount_rate=discount_rate,
                    period_count=period_count, stock_price=stock_price, option=Option.long_put_option(strike_price),
                )
                put_portfolio_tree = put_binomial_tree.calculate_replicating_portfolios()
                put_price = put_portfolio_tree.get_root_portfolio().get_price()

                print("call option price is %f; put option price is %f" % (call_price, put_price))

                # now we have to check that put call parity holds
                strike_price_present_value = strike_price / get_discount_factor(discount_rate) ** period_count

                self.assertAlmostEqual(call_price + strike_price_present_value, put_price + stock_price, delta=1e-9)

    def test_american_option(self):
        for period_count in [3, 8]:
            with self.subTest(period_count):
                total_length = 5
                stock_price = 100
                strike_price = 100
                annual_discount_rate = 0.05
                discount_rate = get_discount_rate(
                    continuous_interest_rate=annual_discount_rate, period_length=total_length / period_count
                )

                crr_parameters = CRRBinomialTreeParameters(
                    stock_price_volatility=0.2, time_horizon=total_length, period_count=period_count
                )
                up_factor, down_factor = crr_parameters.get_up_factor(), crr_parameters.get_down_factor()

                call_binomial_tree = BinomialTreeAmerican(BinomialTreeEuropean(
                    up_factor=up_factor, down_factor=down_factor, period_discount_rate=discount_rate,
                    period_count=period_count, stock_price=stock_price, option=Option.long_call_option(strike_price),
                ))
                call_portfolio_tree = call_binomial_tree.calculate_replicating_portfolios()
                call_price = call_portfolio_tree.get_root_portfolio().get_price()

                put_binomial_tree = BinomialTreeAmerican(BinomialTreeEuropean(
                    up_factor=up_factor, down_factor=down_factor, period_discount_rate=discount_rate,
                    period_count=period_count, stock_price=stock_price, option=Option.long_put_option(strike_price),
                ))
                put_portfolio_tree = put_binomial_tree.calculate_replicating_portfolios()
                put_price = put_portfolio_tree.get_root_portfolio().get_price()

                print("call option price is %f; put option price is %f" % (call_price, put_price))


if __name__ == '__main__':
    unittest.main()
