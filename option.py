class PriceInfo:
    def __init__(self, stock_price, max_encountered):
        self.stock_price = stock_price
        self.max_encountered = max_encountered


class Option:
    OPTION_TYPE_LONG_CALL = 1
    OPTION_TYPE_LONG_PUT = 2
    OPTION_TYPE_SHORT_CALL = 3
    OPTION_TYPE_SHORT_PUT = 4

    @classmethod
    def long_call_option(cls, strike_price):
        return cls(Option.OPTION_TYPE_LONG_CALL, strike_price)

    @classmethod
    def long_put_option(cls, strike_price):
        return cls(Option.OPTION_TYPE_LONG_PUT, strike_price)

    @classmethod
    def short_call_option(cls, strike_price):
        return cls(Option.OPTION_TYPE_SHORT_CALL, strike_price)

    @classmethod
    def short_put_option(cls, strike_price):
        return cls(Option.OPTION_TYPE_SHORT_PUT, strike_price)

    def __init__(self, option_type, strike_price):
        self.option_type = option_type
        self.strike_price = strike_price

    def get_payout(self, price_info: PriceInfo):
        stock_price = price_info.stock_price

        if self.option_type == Option.OPTION_TYPE_LONG_CALL:
            return 0 if stock_price < self.strike_price else stock_price - self.strike_price
        elif self.option_type == Option.OPTION_TYPE_SHORT_CALL:
            return 0 if stock_price < self.strike_price else self.strike_price - stock_price
        elif self.option_type == Option.OPTION_TYPE_LONG_PUT:
            return 0 if stock_price > self.strike_price else self.strike_price - stock_price
        elif self.option_type == Option.OPTION_TYPE_SHORT_PUT:
            return 0 if stock_price > self.strike_price else stock_price - self.strike_price
        else:
            raise RuntimeError("unexpected option type %d", self.option_type)


class BarrierOption:
    def __init__(self, option, barrier_price):
        self.option = option
        self.barrier_price = barrier_price

    def get_payout(self, price_info: PriceInfo):
        if price_info.max_encountered < self.barrier_price:
            return 0

        return self.option.get_payout(price_info)
