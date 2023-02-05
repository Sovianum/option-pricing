import unittest
import numpy as np
from crr import CRRBinomialTreeParameters


class TestCRR(unittest.TestCase):
    def test_zero_volatility_and_discount(self):
        crr = CRRBinomialTreeParameters(0, 0, 1, 1)

        self.assertAlmostEqual(1, crr.get_up_factor(), delta=1e-9)
        self.assertAlmostEqual(1, crr.get_down_factor(), delta=1e-9)
        self.assertAlmostEqual(0, crr.get_discount_rate(), delta=1e-9)

    def test_non_zero_volatility(self):
        crr = CRRBinomialTreeParameters(np.log(2), 0, 1, 1)

        self.assertAlmostEqual(2, crr.get_up_factor(), delta=1e-9)
        self.assertAlmostEqual(1 / 2, crr.get_down_factor(), delta=1e-9)
        self.assertAlmostEqual(0, crr.get_discount_rate(), delta=1e-9)

    def test_non_zero_discount(self):
        crr = CRRBinomialTreeParameters(0, np.log(2), 1, 1)

        self.assertAlmostEqual(1, crr.get_up_factor(), delta=1e-9)
        self.assertAlmostEqual(1, crr.get_down_factor(), delta=1e-9)
        self.assertAlmostEqual(1, crr.get_discount_rate(), delta=1e-9)

    def test_multi_step_volatility(self):
        crr = CRRBinomialTreeParameters(1, 0, 10 * np.log(3) ** 2, 10)

        self.assertAlmostEqual(3, crr.get_up_factor(), delta=1e-9)
        self.assertAlmostEqual(1 / 3, crr.get_down_factor(), delta=1e-9)
        self.assertAlmostEqual(0, crr.get_discount_rate(), delta=1e-9)

    def test_multi_step_discount(self):
        crr = CRRBinomialTreeParameters(0, 1, 10 * np.log(3), 10)

        self.assertAlmostEqual(1, crr.get_up_factor(), delta=1e-9)
        self.assertAlmostEqual(1, crr.get_down_factor(), delta=1e-9)
        self.assertAlmostEqual(2, crr.get_discount_rate(), delta=1e-9)


if __name__ == '__main__':
    unittest.main()
