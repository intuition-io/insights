'''
Tests for insights.sources.live.fake
'''

import unittest
from nose.tools import nottest, eq_, ok_
import pandas as pd
import insights.sources.live.fake as fake


class RandomTestCase(unittest.TestCase):

    def setUp(self):
        self.sids = ['goog', 'aapl']
        self.source = fake.Random(self.sids, {})

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
        data = self.source.get_data(self.sids)
        self.assertIsInstance(data, pd.DataFrame)
        ok_(sorted(data.columns) == sorted(self.sids))
        ok_((data.axes[0] == ['price', 'volume']).all())

    def test_generated_data_is_random(self):
        data = self.source.get_data(self.sids)
        for _ in range(20):
            for sid in self.sids:
                self.assertIsInstance(data[sid].price, float)
                self.assertIsInstance(data[sid].volume, float)
