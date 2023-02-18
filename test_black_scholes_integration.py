import unittest

import black_scholes
import pandas as pd
import numpy as np


class TestBinomialTree(unittest.TestCase):
    def test_calculate_portfolio_price(self):
        stock_price = 230
        risk_free_rate = 5e-3
        volatility = 0.3

        book = pd.DataFrame({
            "amount": [34_000, 37_000, 20_000],
            "type": ["call", "put", "call"],
            "strike_price": [235, 231, 234],
            "maturity": np.array([1, 2, 2]) / 12
        })

        black_and_scholes_option = black_scholes.Option()

        black_scholes_prices = []
        for amount, typ, strike_price, maturity in zip(book.amount, book.type, book.strike_price, book.maturity):
            bs_price = None
            if typ == "call":
                bs_price = black_and_scholes_option.get_call_price(black_scholes.Option.OptionParameters(
                    stock_price=stock_price,
                    strike_price=strike_price,
                    risk_free_rate=risk_free_rate,
                    volatility=volatility,
                    maturity_period_count=
                ))
            else:
                bs_price = black_and_scholes_option.get_put_price(black_scholes.Option.OptionParameters(

                ))


        black_and_scholes_option.get_call_price(black_scholes.Option.OptionParameters(
            stock_price, strike_price, period_discount_rate, stock_price_volatility, time_horizon
        ))


if __name__ == '__main__':
    unittest.main()