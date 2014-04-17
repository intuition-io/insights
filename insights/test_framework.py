'''
Test framework for intuition managers
'''

import unittest
from nose.tools import ok_, nottest
#import pytz
#import pandas as pd
import datetime as dt
#from intuition.api.datafeed import HybridDataFactory
#from intuition.data.universe import Market
# TODO Use FakeDataSource when available
#from insights.sources.backtest.yahoo import YahooPrices
from dna.test_utils import setup_logger, teardown_logger


class FactoryAlgorithmTestCase(unittest.TestCase):

    def setUp(self):
        setup_logger(self)
        '''
        market = Market()
        market.parse_universe_description('stocks:paris:cac40,5')
        self.datafeed = HybridDataFactory(
            index=pd.date_range('2012/01/01', '2012/01/10', tz=pytz.utc),
            universe=market,
            backtest=YahooPrices
        )
        '''

    def tearDown(self):
        teardown_logger(self)


class FactoryManagerTestCase(unittest.TestCase):

    def setUp(self):
        setup_logger(self)
        self.some_date = dt.datetime(2014, 04, 10)
        # TODO Use true portfolio positions
        self.buy_signal = {'goog': 34}

    def tearDown(self):
        teardown_logger(self)

    @nottest
    def _check_initialization(self, manager):
        ok_(not manager.date)
        ok_(not manager.portfolio)
        ok_(not manager.perfs)
        ok_(hasattr(manager, 'log'))

    @nottest
    def _check_optimize_return(self, alloc, e_ret, e_risk):
        ok_(isinstance(alloc, dict))
        ok_(e_ret >= 0 and e_ret <= 1)
        ok_(e_risk >= 0 and e_risk <= 1)
