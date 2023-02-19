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

    def delta_call(self, parameters, step=1e-3):
        return self._delta(parameters, self.get_call_price, step)

    def delta_put(self, parameters, step=1e-3):
        return self._delta(parameters, self.get_put_price, step)

    def gamma_call(self, parameters, step=1e-3):
        return self._gamma(parameters, self.get_call_price, step)

    def gamma_put(self, parameters, step=1e-3):
        return self._gamma(parameters, self.get_put_price, step)

    def theta_call(self, parameters, step=1e-3):
        return self._theta(parameters, self.get_call_price, step)

    def theta_put(self, parameters, step=1e-3):
        return self._theta(parameters, self.get_put_price, step)

    def vega_call(self, parameters, step=1e-3):
        return self._vega(parameters, self.get_call_price, step)

    def vega_put(self, parameters, step=1e-3):
        return self._vega(parameters, self.get_put_price, step)

    def rho_call(self, parameters, step=1e-3):
        return self._rho(parameters, self.get_call_price, step)

    def rho_put(self, parameters, step=1e-3):
        return self._rho(parameters, self.get_put_price, step)

    def _delta(self, parameters, price_callback, step):
        left_price = price_callback(parameters.copy(stock_price_offset=-step))
        right_price = price_callback(parameters.copy(stock_price_offset=step))

        return (right_price - left_price) / (2 * step)

    def _gamma(self, parameters, price_callback, step):
        left_price = price_callback(parameters.copy(stock_price_offset=-step))
        center_price = price_callback(parameters.copy())
        right_price = price_callback(parameters.copy(stock_price_offset=step))

        return (right_price - 2 * center_price + left_price) / (4 * step**2)

    def _theta(self, parameters, price_callback, step):
        left_price = price_callback(parameters.copy(maturity_time_offset=-step))
        right_price = price_callback(parameters.copy(maturity_time_offset=step))

        return (right_price - left_price) / (2 * step)

    def _vega(self, parameters, price_callback, step):
        left_price = price_callback(parameters.copy(volatility_offset=-step))
        right_price = price_callback(parameters.copy(volatility_offset=step))

        return (right_price - left_price) / (2 * step)

    def _rho(self, parameters, price_callback, step):
        left_price = price_callback(parameters.copy(risk_free_rate_offset=-step))
        right_price = price_callback(parameters.copy(risk_free_rate_offset=step))

        return (right_price - left_price) / (2 * step)

    def _d2(self, parameters):
        return self._d1(parameters) - parameters.volatility * np.sqrt(parameters.maturity_time)

    def _d1(self, parameters):
        return 1 / (parameters.volatility * np.sqrt(parameters.maturity_time)) * (
                np.log(parameters.stock_price / parameters.strike_price) + (parameters.risk_free_rate + 1/2 * parameters.volatility**2) * parameters.maturity_time
        )
