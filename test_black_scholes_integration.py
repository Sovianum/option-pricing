import unittest

import black_scholes
import pandas as pd
import numpy as np
from greek_calculator import GreekCalculator
pd.set_option('display.max_columns', None)


class TestBinomialTree(unittest.TestCase):
    risk_free_rate = 5e-3
    original_stock_price = 230
    original_volatility = 0.3

    delta_maturity = -1 / 365
    delta_stock_price = 6
    delta_volatility = 100e-4

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

    def test_calculate_price_neutral_portfolio(self):
        non_neutral_portfolio = self.original_book.copy()
        non_neutral_portfolio.maturity += self.delta_maturity
        non_neutral_portfolio = self.fill_book(
            non_neutral_portfolio,
            self.original_stock_price + self.delta_stock_price,
            self.original_volatility + self.delta_volatility,
        )

        original_delta = sum(non_neutral_portfolio.delta * non_neutral_portfolio.amount)
        original_gamma = sum(non_neutral_portfolio.gamma * non_neutral_portfolio.amount)

        neutralization_portfolio = self.fill_book(
            pd.DataFrame({
                "amount": [1, 1],
                "type": ["call", "put"],
                "strike_price": [235, self.original_stock_price + self.delta_stock_price],
                "maturity": np.array([4, 3]) / 12
            }),
            self.original_stock_price + self.delta_stock_price,
            self.original_volatility + self.delta_volatility
        )

        parameter_matrix = np.array([
            neutralization_portfolio.delta,
            neutralization_portfolio.gamma
        ])

        non_neutral_parameters = np.array([
            original_delta,
            original_gamma
        ])

        neutralization_weights = np.matmul(
            np.linalg.inv(parameter_matrix),
            -non_neutral_parameters
        )

        # now we recalculate neutralization portfolio using given weights

        neutralization_portfolio = self.fill_book(
            pd.DataFrame({
                "amount": neutralization_weights,
                "type": ["call", "put"],
                "strike_price": [235, self.original_stock_price + self.delta_stock_price],
                "maturity": np.array([4, 3]) / 12
            }),
            self.original_stock_price + self.delta_stock_price,
            self.original_volatility + self.delta_volatility
        )

        non_neutral_price = sum(non_neutral_portfolio.total_prices)

        hedging_cost = neutralization_portfolio.total_prices.sum()

        neutralized_portfolio = pd.concat([non_neutral_portfolio, neutralization_portfolio]).reset_index().drop(columns=["index"])

        def get_total_parameter(name):
            return [(neutralized_portfolio[name] * neutralized_portfolio.amount).sum()]

        neutralized_portfolio_parameters = pd.DataFrame({
            "delta": get_total_parameter("delta"),
            "gamma": get_total_parameter("gamma"),
            "theta": get_total_parameter("theta"),
            "vega": get_total_parameter("vega"),
            "rho": get_total_parameter("rho")
        })

        print("parameter matrix")
        print(parameter_matrix)
        print("non neutral parameters")
        print(non_neutral_parameters)
        print("neutralization weights")
        print(neutralization_weights)
        print("hedging cost")
        print(hedging_cost)
        print("non neutral price")
        print(non_neutral_price)
        print("neutralization prices")
        print(neutralization_portfolio.prices)
        print("hedging cost")
        print(hedging_cost)
        print("neutralized portfolio parameters")
        print(neutralized_portfolio_parameters.round().to_latex())

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

            price_callback = bs_option.get_call_price if typ == "call" else bs_option.get_put_price

            calculator = GreekCalculator(price_callback)

            bs_prices.append(price_callback(parameters))
            deltas.append(calculator.delta(parameters))
            gammas.append(calculator.gamma(parameters))
            thetas.append(calculator.theta(parameters))
            vegas.append(calculator.vega(parameters))
            rhos.append(calculator.rho(parameters))

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