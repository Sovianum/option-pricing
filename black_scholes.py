import numpy as np
import scipy.stats


class Option:
    class OptionParameters:
        def __init__(self, stock_price, strike_price, risk_free_rate, volatility, maturity_time):
            self.stock_price = stock_price
            self.strike_price = strike_price
            self.risk_free_rate = risk_free_rate
            self.volatility = volatility
            self.maturity_time = maturity_time

        def copy(self, stock_price_offset=0, strike_price_offset=0, risk_free_rate_offset=0, volatility_offset=0,
                 maturity_time_offset=0):

            return Option.OptionParameters(
                self.stock_price + stock_price_offset,
                self.strike_price + strike_price_offset,
                self.risk_free_rate + risk_free_rate_offset,
                self.volatility + volatility_offset,
                self.maturity_time + maturity_time_offset
            )

    def get_call_price(self, parameters):
        d1 = self._d1(parameters)
        d2 = self._d2(parameters)

        stock_term = parameters.stock_price * scipy.stats.norm.cdf(d1)
        bond_term = np.exp(-parameters.risk_free_rate * parameters.maturity_time) * parameters.strike_price * scipy.stats.norm.cdf(d2)

        return stock_term - bond_term

    def get_put_price(self, parameters):
        d1 = self._d1(parameters)
        d2 = self._d2(parameters)

        bond_term = np.exp(parameters.risk_free_rate * parameters.maturity_time) * parameters.strike_price * scipy.stats.norm.cdf(-d2)
        stock_term = parameters.stock_price * scipy.stats.norm.cdf(-d1)

        return bond_term - stock_term

    def _d2(self, parameters):
        return self._d1(parameters) - parameters.volatility * np.sqrt(parameters.maturity_time)

    def _d1(self, parameters):
        return 1 / (parameters.volatility * np.sqrt(parameters.maturity_time)) * (
                np.log(parameters.stock_price / parameters.strike_price) + (parameters.risk_free_rate + 1/2 * parameters.volatility**2) * parameters.maturity_time
        )
