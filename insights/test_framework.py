# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Test framework for insights modules
  -----------------------------------

  :copyright (c) 2014 Xavier Bruhiere
  :license: Apache 2.0, see LICENSE for more details.
'''

import abc
import unittest
from nose.tools import ok_, nottest
import pytz
import pandas as pd
import datetime as dt
import random
import yaml
import zipline.protocol
from dna.test_utils import setup_logger, teardown_logger


def _generate_sid_data(sid):
    return {
        'source_id': __name__ + '-1234',
        'type': 4,
        'sid': sid,
        'dt': pd.tslib.Timestamp('2012/06/05', tz=pytz.utc),
        'datetime': pd.tslib.Timestamp('2012/06/05', tz=pytz.utc),
        'price': random.random() * 10,
        'volume': random.random() * 1000
    }


def generate_fake_returns(sids):
    dates = pd.date_range('2012/01/01', '2012/06/01', tz=pytz.utc)
    return pd.DataFrame(
        {sid: [random.random() * 100 for _ in range(len(dates))]
            for sid in sids},
        index=dates
    )


def generate_portfolio(sids):
    ''' Build a random, zipline compliant portfolio '''
    pf = zipline.protocol.Portfolio()
    if isinstance(sids, list):
        sids = {sid: random.randint(1, 100) for sid in sids}

    for sid, amount in sids.iteritems():
        pf.positions[sid] = zipline.protocol.Position(sid)
        pf.positions[sid].amount = amount
        cost = random.randrange(1, 200)
        pf.positions[sid].cost_basis = cost
        pf.positions[sid].last_sale_price = random.randrange(
            int(cost), int(cost + 1000 * random.random())
        )

    return pf


# pylint: disable=R0921
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
        for info in _generate_sid_data('').keys():
            self.assertIn(info, sid_data)

    def _check_event_output(self, signals):
        if signals is not None:
            self.assertIsInstance(signals, dict)
            for signal_type in ['buy', 'sell']:
                for sid in signals.get(signal_type, {}):
                    self._check_signal_sid(signals[signal_type][sid])


# pylint: disable=R0921
class FactoryManagerTestCase(unittest.TestCase):
    '''
    This abstract factory class targets the same achievements as the
    FactoryAlgorithmTestCase, focusing on Intuition managers building block.
    '''

    __metaclass__ = abc.ABCMeta

    def setUp(self):
        setup_logger(self)
        self.some_date = dt.datetime(2014, 04, 10)
        self.buy_signal = {'goog': 34}
        self.test_sids = ['goog', 'aapl', 'msft']
        self.test_pf = generate_portfolio(self.test_sids)

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
