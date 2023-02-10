import unittest
import numpy as np
from utils import get_discount_rate


class TestDiscountRate(unittest.TestCase):
    def test_zero_discount(self):
        self.assertAlmostEqual(0, get_discount_rate(0, 1), delta=1e-9)

    def test_non_zero_discount(self):
        self.assertAlmostEqual(1, get_discount_rate(np.log(2), 1), delta=1e-9)


if __name__ == '__main__':
    unittest.main()
