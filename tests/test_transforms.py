'''
Tests for insights.transforms
'''

import unittest
from nose.tools import ok_, eq_, nottest, raises
import insights.transforms as transforms


class TransformsTestCase(unittest.TestCase):

    @nottest
    def _check_intialized_transform(self, past_prices):
        eq_(past_prices.bars, 'daily')
        eq_(past_prices.bars_in_day, 1)
        eq_(past_prices.trading_days_total, 0)
        ok_(past_prices.compute_only_full)
        ok_(not past_prices.full)
        ok_(not past_prices.updated)

    def test_intialize_get_past_prices(self):
        past_prices = transforms.get_past_prices(
            refresh_period=10,
            window_length=20,
            compute_only_full=True
        )
        self._check_intialized_transform(past_prices)
        eq_(past_prices.compute_transform_value({'price': 5.32}), 5.32)
        eq_(past_prices.refresh_period, 10)
        eq_(past_prices.window_length, 20)

    @raises(NotImplementedError)
    def test_not_implemented_get_value(self):
        past_prices = transforms.get_past_prices(
            refresh_period=10,
            window_length=20,
            compute_only_full=True
        )
        past_prices.get_value()
