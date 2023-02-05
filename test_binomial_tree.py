import unittest
import numpy as np
from binomial_tree import BinomialTree
from option import Option


class TestBinomialTree(unittest.TestCase):
    def test_get_leaf_node_price_factors(self):
        price_factors = BinomialTree.get_leaf_node_price_factors(3, 2, 1)

        self.assertTrue(
            (np.array([8, 4, 4, 2, 4, 2, 2, 1]) == price_factors).all()
        )

    def test_option_pricing_no_discounting(self):
        tree = BinomialTree(2, 0.5, 0, 2, 1, Option.long_call_option(0.5))
        portfolio_tree = tree.calculate_replicating_portfolios_european()

        portfolio_up = portfolio_tree.get_portfolio(1, 0)
        self.assertAlmostEqual(2, portfolio_up.share_weight, delta=1e-9)
        self.assertAlmostEqual(-0.5, portfolio_up.bond_weight, delta=1e-9)
        self.assertAlmostEqual(1.5, portfolio_up.get_price(), delta=1e-9)

        portfolio_down = portfolio_tree.get_portfolio(1, 1)
        self.assertAlmostEqual(1 / 3, portfolio_down.share_weight, delta=1e-9)
        self.assertAlmostEqual(-1 / 6, portfolio_down.bond_weight, delta=1e-9)
        self.assertAlmostEqual(1 / 6, portfolio_down.get_price(), delta=1e-9)

        portfolio_root = portfolio_tree.get_portfolio(0, 0)
        self.assertAlmostEqual(2 / 3, portfolio_root.share_weight, delta=1e-9)
        self.assertAlmostEqual(-1 / 3, portfolio_root.bond_weight, delta=1e-9)
        self.assertAlmostEqual(1 / 3, portfolio_root.get_price(), delta=1e-9)

    def test_stock_price_scaling(self):
        tree = BinomialTree(2, 0.5, 0, 1, 100, Option.long_call_option(100))
        portfolio_tree = tree.calculate_replicating_portfolios_european()

        portfolio = portfolio_tree.get_root()
        self.assertAlmostEqual(2 / 3, portfolio.share_weight, delta=1e-9)
        self.assertAlmostEqual(-1 / 3, portfolio.bond_weight, delta=1e-9)
        self.assertAlmostEqual(1 / 3, portfolio.get_norm_price(), delta=1e-9)
        self.assertAlmostEqual(1 / 3 * 100, portfolio.get_price(), delta=1e-9)

    def test_discounting_factor(self):
        tree = BinomialTree(2, 0.5, 0.5, 1, 100, Option.long_call_option(100))
        portfolio_tree = tree.calculate_replicating_portfolios_european()

        portfolio = portfolio_tree.get_root()
        self.assertAlmostEqual(2 / 3, portfolio.share_weight, delta=1e-9)
        self.assertAlmostEqual(-2 / 9, portfolio.bond_weight, delta=1e-9)
        self.assertAlmostEqual(4 / 9, portfolio.get_norm_price(), delta=1e-9)
        self.assertAlmostEqual(4 / 9 * 100, portfolio.get_price(), delta=1e-9)


if __name__ == '__main__':
    unittest.main()
