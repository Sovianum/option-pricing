import unittest
from binomial_tree_american import BinomialTreeAmerican
from binomial_tree_european import BinomialTreeEuropean
from option import Option, BarrierOption


class TestBinomialTree(unittest.TestCase):
    def test_option_pricing_no_discounting_european(self):
        tree = BinomialTreeEuropean(2, 0.5, 0, 2, 1, Option.long_call_option(0.5))
        portfolio_tree = tree.calculate_replicating_portfolios()

        portfolio_up = portfolio_tree.get_portfolio(1, 0)
        self.assertAlmostEqual(1, portfolio_up.share_weight, delta=1e-9)
        self.assertAlmostEqual(-0.25, portfolio_up.bond_weight, delta=1e-9)
        self.assertAlmostEqual(1.5, portfolio_up.get_price(), delta=1e-9)

        portfolio_down = portfolio_tree.get_portfolio(1, 1)
        self.assertAlmostEqual(2 / 3, portfolio_down.share_weight, delta=1e-9)
        self.assertAlmostEqual(-1 / 3, portfolio_down.bond_weight, delta=1e-9)
        self.assertAlmostEqual(1 / 6, portfolio_down.get_price(), delta=1e-9)

        portfolio_root = portfolio_tree.get_portfolio(0, 0)
        self.assertAlmostEqual(8 / 9, portfolio_root.share_weight, delta=1e-9)
        self.assertAlmostEqual(-5 / 18, portfolio_root.bond_weight, delta=1e-9)
        self.assertAlmostEqual(11 / 18, portfolio_root.get_price(), delta=1e-9)

    def test_option_pricing_no_discounting_european_from_lecture(self):
        tree = BinomialTreeEuropean(1.1, 0.9, 0.05, 2, 100, Option.long_call_option(100))
        portfolio_tree = tree.calculate_replicating_portfolios()

        portfolio_up = portfolio_tree.get_portfolio(1, 0)
        self.assertAlmostEqual(0.955, portfolio_up.share_weight, delta=1e-2)
        self.assertAlmostEqual(-90/110, portfolio_up.bond_weight, delta=1e-9)
        self.assertAlmostEqual(15, portfolio_up.get_price(), delta=1e-9)

        portfolio_down = portfolio_tree.get_portfolio(1, 1)
        self.assertAlmostEqual(0, portfolio_down.share_weight, delta=1e-9)
        self.assertAlmostEqual(0, portfolio_down.bond_weight, delta=1e-9)
        self.assertAlmostEqual(0, portfolio_down.get_price(), delta=1e-9)

        portfolio_root = portfolio_tree.get_portfolio(0, 0)
        self.assertAlmostEqual(0.75, portfolio_root.share_weight, delta=1e-9)
        self.assertAlmostEqual(-64.28/100, portfolio_root.bond_weight, delta=1e-2)
        self.assertAlmostEqual(10.72, portfolio_root.get_price(), delta=1e-2)

    def test_option_pricing_no_discounting_american(self):
        tree = BinomialTreeAmerican(BinomialTreeEuropean(1.1, 0.9, 0.05, 2, 100, Option.long_put_option(100)))
        portfolio_tree = tree.calculate_replicating_portfolios()

        portfolio_up = portfolio_tree.get_portfolio(1, 0)
        self.assertAlmostEqual(0.238, portfolio_up.get_price(), delta=1e-4)

        portfolio_down = portfolio_tree.get_portfolio(1, 1)
        self.assertAlmostEqual(10, portfolio_down.get_price(), delta=1e-9)

        portfolio_root = portfolio_tree.get_portfolio(0, 0)
        self.assertAlmostEqual(2.551, portfolio_root.get_price(), delta=1e-3)

    def test_option_pricing_no_discounting_barrier(self):
        tree = BinomialTreeEuropean(1.1, 0.9, 0, 2, 100, BarrierOption(Option.long_put_option(100), 101))
        portfolio_tree = tree.calculate_replicating_portfolios()

        portfolio_up = portfolio_tree.get_portfolio(1, 0)
        self.assertAlmostEqual(0.5, portfolio_up.get_price(), delta=1e-9)

        portfolio_down = portfolio_tree.get_portfolio(1, 1)
        self.assertAlmostEqual(0, portfolio_down.get_price(), delta=1e-9)

        portfolio_root = portfolio_tree.get_portfolio(0, 0)
        self.assertAlmostEqual(0.25, portfolio_root.get_price(), delta=1e-9)

    def test_stock_price_scaling_european(self):
        tree = BinomialTreeEuropean(2, 0.5, 0, 1, 100, Option.long_call_option(100))
        portfolio_tree = tree.calculate_replicating_portfolios()

        portfolio = portfolio_tree.get_root_portfolio()
        self.assertAlmostEqual(2 / 3, portfolio.share_weight, delta=1e-9)
        self.assertAlmostEqual(-1 / 3, portfolio.bond_weight, delta=1e-9)
        self.assertAlmostEqual(1 / 3 * 100, portfolio.get_price(), delta=1e-9)

    def test_discounting_factor_european(self):
        tree = BinomialTreeEuropean(2, 0.5, 0.5, 1, 100, Option.long_call_option(100))
        portfolio_tree = tree.calculate_replicating_portfolios()

        portfolio = portfolio_tree.get_root_portfolio()
        self.assertAlmostEqual(2 / 3, portfolio.share_weight, delta=1e-9)
        self.assertAlmostEqual(-2 / 9, portfolio.bond_weight, delta=1e-9)
        self.assertAlmostEqual(4 / 9 * 100, portfolio.get_price(), delta=1e-9)


if __name__ == '__main__':
    unittest.main()
