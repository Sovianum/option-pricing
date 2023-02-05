import unittest
from option import Option


class TestOption(unittest.TestCase):
    def test_long_call(self):
        option = Option.long_call_option(100)
        self.assertEqual(option.get_payout(200), 100)
        self.assertEqual(option.get_payout(50), 0)

    def test_short_call(self):
        option = Option.short_call_option(100)
        self.assertEqual(option.get_payout(200), -100)
        self.assertEqual(option.get_payout(50), 0)

    def test_long_put(self):
        option = Option.long_put_option(100)
        self.assertEqual(option.get_payout(200), 0)
        self.assertEqual(option.get_payout(50), 50)

    def test_short_put(self):
        option = Option.short_put_option(100)
        self.assertEqual(option.get_payout(200), 0)
        self.assertEqual(option.get_payout(50), -50)


if __name__ == '__main__':
    unittest.main()
