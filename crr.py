import numpy as np


class CRRBinomialTreeParameters:
    def __init__(self, stock_price_volatility, continuous_interest_rate, time_horizon, period_count):
        self.stock_price_volatility = stock_price_volatility
        self.continuous_interest_rate = continuous_interest_rate
        self.time_horizon = time_horizon
        self.period_count = period_count

    def get_up_factor(self):
        return np.exp(self.stock_price_volatility * np.sqrt(self._get_period_length()))

    def get_down_factor(self):
        return 1 / self.get_up_factor()

    def get_discount_rate(self):
        return np.exp(self.continuous_interest_rate * self._get_period_length()) - 1

    def _get_period_length(self):
        return self.time_horizon / self.period_count
