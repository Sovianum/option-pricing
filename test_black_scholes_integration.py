import unittest

import black_scholes
import pandas as pd
import numpy as np
pd.set_option('display.max_columns', None)


class TestBinomialTree(unittest.TestCase):
    risk_free_rate = 5e-3
    original_stock_price = 230
    original_volatility = 0.3

    delta_maturity = -1 / 365
    # delta_maturity = 0
    delta_stock_price = 6
    # delta_stock_price = 2
    delta_volatility = 100e-4
    # delta_volatility = 0

    original_book = pd.DataFrame({
        "amount": [34_000, 37_000, 20_000],
        "type": ["call", "put", "call"],
        "strike_price": [235, 231, 234],
        "maturity": np.array([1, 2, 2]) / 12
    })

    def test_calculate_portfolio_price(self):
        original_book = self.fill_book(self.original_book, self.original_stock_price, self.original_volatility)

        print(original_book)
        print(original_book[["prices", "total_prices", "delta", "gamma", "theta", "vega", "rho"]].to_latex())
        print(original_book.total_prices.sum())

    def test_calculate_pnl_linear(self):
        original_book = self.fill_book(self.original_book, self.original_stock_price, self.original_volatility)

        price_diff_df = pd.DataFrame({
            "maturity_term": original_book.amount * original_book.theta * self.delta_maturity,
            "first_order_stock_price_term": original_book.amount * original_book.delta * self.delta_stock_price,
            "second_order_stock_price_term": original_book.amount * 0.5 * original_book.gamma * self.delta_stock_price**2,
            "volatility_term": original_book.amount * original_book.vega * self.delta_volatility
        })

        print(price_diff_df.round().to_latex())
        print(price_diff_df.round().sum())
        print(price_diff_df.round().sum().sum())

    def test_non_linearity(self):
        yesterday_book = self.original_book.copy()
        yesterday_book = self.fill_book(yesterday_book, self.original_stock_price, self.original_volatility)

        today_book = self.original_book.copy()
        today_book = self.fill_book(
            today_book,
            self.original_stock_price + self.delta_stock_price,
            self.original_volatility
        )

        linear_diff_1 = yesterday_book.delta * self.delta_stock_price
        # linear_diff_2 = 0.5 * yesterday_book.gamma * self.delta_stock_price**2
        linear_diff_2 = 0

        diff_df = pd.DataFrame({
            "non_linear_diff": today_book.prices - yesterday_book.prices,
            "linear_diff": linear_diff_1 + linear_diff_2
        })
        diff_df["err_percent"] = (diff_df.non_linear_diff - diff_df.linear_diff) / diff_df.non_linear_diff * 100

        print(diff_df)
        print(diff_df.sum())

    def test_calculate_pnl_non_linear(self):
        yesterday_book = self.original_book
        yesterday_book = self.fill_book(yesterday_book, self.original_stock_price, self.original_volatility)

        today_book = self.original_book.copy()
        today_book.maturity += self.delta_maturity
        today_book = self.fill_book(
            today_book,
            self.original_stock_price + self.delta_stock_price,
            self.original_volatility + self.delta_volatility,
        )

        price_diff_df = pd.DataFrame({
            "total_price_0": yesterday_book.total_prices,
            "total_price_1": today_book.total_prices
        })
        price_diff_df["diff"] = price_diff_df.total_price_1 - price_diff_df.total_price_0
        print(price_diff_df.to_latex())
        print(price_diff_df["diff"].sum())

    def fill_book(self, book, stock_price, volatility):
        bs_option = black_scholes.Option()

        bs_prices = []
        deltas = []
        gammas = []
        thetas = []
        vegas = []
        rhos = []
        for amount, typ, strike_price, maturity in zip(book.amount, book.type, book.strike_price, book.maturity):
            parameters = black_scholes.Option.OptionParameters(
                stock_price=stock_price,
                strike_price=strike_price,
                risk_free_rate=self.risk_free_rate,
                volatility=volatility,
                maturity_time=maturity
            )

            is_call = typ == "call"

            bs_prices.append(
                bs_option.get_call_price(parameters) if is_call else bs_option.get_put_price(parameters)
            )
            deltas.append(
                bs_option.delta_call(parameters) if is_call else bs_option.delta_put(parameters)
            )
            gammas.append(
                bs_option.gamma_call(parameters) if is_call else bs_option.gamma_put(parameters)
            )
            thetas.append(
                bs_option.theta_call(parameters) if is_call else bs_option.theta_put(parameters)
            )
            vegas.append(
                bs_option.vega_call(parameters) if is_call else bs_option.vega_put(parameters)
            )
            rhos.append(
                bs_option.rho_call(parameters) if is_call else bs_option.rho_put(parameters)
            )

        book["prices"] = bs_prices
        book["total_prices"] = book.amount * book.prices
        book["delta"] = deltas
        book["gamma"] = gammas
        book["theta"] = thetas
        book["vega"] = vegas
        book["rho"] = rhos

        return book


if __name__ == '__main__':
    unittest.main()