

class GreekCalculator:
    def __init__(self, price_callback):
        self.price_callback = price_callback

    def delta(self, parameters, step=1e-3):
        left_price = self.price_callback(parameters.copy(stock_price_offset=-step))
        right_price = self.price_callback(parameters.copy(stock_price_offset=step))

        return (right_price - left_price) / (2 * step)

    def gamma(self, parameters, step=1e-3):
        left_price = self.price_callback(parameters.copy(stock_price_offset=-step))
        center_price = self.price_callback(parameters.copy())
        right_price = self.price_callback(parameters.copy(stock_price_offset=step))

        return (right_price - 2 * center_price + left_price) / (4 * step**2)

    def theta(self, parameters, step=1e-3):
        left_price = self.price_callback(parameters.copy(maturity_time_offset=-step))
        right_price = self.price_callback(parameters.copy(maturity_time_offset=step))

        return (right_price - left_price) / (2 * step)

    def vega(self, parameters, step=1e-3):
        left_price = self.price_callback(parameters.copy(volatility_offset=-step))
        right_price = self.price_callback(parameters.copy(volatility_offset=step))

        return (right_price - left_price) / (2 * step)

    def rho(self, parameters, step=1e-3):
        left_price = self.price_callback(parameters.copy(risk_free_rate_offset=-step))
        right_price = self.price_callback(parameters.copy(risk_free_rate_offset=step))

        return (right_price - left_price) / (2 * step)
