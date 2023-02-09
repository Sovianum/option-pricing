def get_risk_neutral_probability(discount_rate, up_factor, down_factor):
    return (1 + discount_rate - down_factor) / (up_factor - down_factor)
