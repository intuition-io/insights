'''
Tests for insights.sources.backtest.yahoo
'''

import unittest
from nose.tools import nottest, eq_
import insights.sources.backtest.yahoo as yahoo


class YahooPricesTestCase(unittest.TestCase):

    def setUp(self):
        self.sids = ['goog', 'aapl']
        self.start = '2012/01/01'
        self.end = '2012/06/01'
        self.source = yahoo.YahooPrices(self.sids, {})

    @nottest
    def _check_mapping(self, mapping):
        self.assertIsInstance(mapping, dict)
        eq_(sorted(mapping.keys()),
            sorted(['dt', 'sid', 'price', 'volume']))
        for key, pair in mapping.iteritems():
            self.assertIsInstance(pair, tuple)
            self.assertIsInstance(pair[1], str)

    def test_intialize(self):
        self._check_mapping(self.source.mapping)

    def test_generate_data(self):
        # FIXME Functionnal test which uses the network
        pass
