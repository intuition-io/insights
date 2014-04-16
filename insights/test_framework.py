'''
Test framework for intuition managers
'''

import unittest
from nose.tools import ok_, nottest
import datetime as dt
from dna.test_utils import setup_logger, teardown_logger


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
