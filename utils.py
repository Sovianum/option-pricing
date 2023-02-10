import numpy as np


def get_discount_rate(continuous_interest_rate, period_length):
    return np.log(1 + continuous_interest_rate) * period_length


def get_discount_factor(discount_rate):
    return np.exp(discount_rate)


def get_risk_neutral_probability(discount_rate, up_factor, down_factor):
    return (get_discount_factor(discount_rate) - down_factor) / (up_factor - down_factor)
