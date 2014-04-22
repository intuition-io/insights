'''
Test framework for intuition managers
'''

import abc
import unittest
from nose.tools import ok_, nottest
import pytz
import pandas as pd
import datetime as dt
from random import random
import yaml
#from intuition.api.datafeed import HybridDataFactory
#from intuition.data.universe import Market
# TODO Use FakeDataSource when available
#from insights.sources.backtest.yahoo import YahooPrices
import zipline.protocol
from dna.test_utils import setup_logger, teardown_logger


def _generate_sid_data(sid):
    return {
        'source_id': __name__ + '-1234',
        'type': 4,
        'sid': sid,
        'dt': pd.tslib.Timestamp('2012/06/05', tz=pytz.utc),
        'datetime': pd.tslib.Timestamp('2012/06/05', tz=pytz.utc),
        'price': random() * 10,
        'volume': random() * 1000
    }


#pylint: disable=R0921
class FactoryAlgorithmTestCase(unittest.TestCase):
    '''
    New algorithm tests inherit from this factory class. The main idea is to
    provide a common ground to validate Intuition compliant algorithms, and
    ease tests writting.
    '''

    __metaclass__ = abc.ABCMeta

    def setUp(self):
        setup_logger(self)
        self.default_identity = 'johndoe'
        self.event_data = zipline.protocol.BarData()
        for sid in ['goog', 'aapl', 'msft']:
            self.event_data[sid] = zipline.protocol.SIDData(
                _generate_sid_data(sid)
            )

    def tearDown(self):
        teardown_logger(self)

    def _check_yaml_doc(self, Algo):
        doc = yaml.load(Algo.__doc__)
        ok_(isinstance(doc, dict))
        self.assertIn('doc', doc)
        ok_(isinstance(doc.get('parameters', {}), dict))

    def _check_signal_sid(self, sid_data):
        self.assertIsInstance(sid_data, zipline.protocol.SIDData)
        #for info in ['volume', 'price', 'dt', 'type', 'sid']:
        for info in _generate_sid_data('').keys():
            self.assertIn(info, sid_data)

    def _check_event_output(self, signals):
        if signals is not None:
            self.assertIsInstance(signals, dict)
            for signal_type in ['buy', 'sell']:
                for sid in signals.get(signal_type, {}):
                    self._check_signal_sid(signals[signal_type][sid])


#pylint: disable=R0921
class FactoryManagerTestCase(unittest.TestCase):
    '''
    This abstract factory class targets the same achievements as the
    FactoryAlgorithmTestCase, focusing on Intuition managers building block.
    '''

    __metaclass__ = abc.ABCMeta

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
