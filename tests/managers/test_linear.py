'''
Tests for insights.managers.linear
'''

from nose.tools import eq_
import insights.managers.linear as linear
from insights.test_framework import FactoryManagerTestCase


class ConstantManagerTestCase(FactoryManagerTestCase):
    default_amount = 100

    def test_initialize(self):
        self._check_initialization(linear.Constant({}))

    def test_optimize_empty_signals(self):
        manager = linear.Constant({})
        alloc, e_ret, e_risk = manager.optimize({}, {})
        self._check_optimize_return(alloc, e_ret, e_risk)
        eq_(alloc, {})
        eq_(e_ret, 0)
        eq_(e_risk, 1)

    def test_optimize_buy_signals(self):
        manager = linear.Constant({})
        alloc, e_ret, e_risk = manager.optimize(
            to_buy=self.buy_signal, to_sell={})
        self._check_optimize_return(alloc, e_ret, e_risk)
        eq_(alloc, {'goog': self.default_amount})

    def test_optimize_buy_signals_custom_amount(self):
        manager = linear.Constant({'buy_amount': 200})
        alloc, e_ret, e_risk = manager.optimize(
            to_buy=self.buy_signal, to_sell={})
        self._check_optimize_return(alloc, e_ret, e_risk)
        eq_(alloc, {'goog': 200})

    def test_optimize_buy_signals_init_custom_amount(self):
        manager = linear.Constant({'buy_amount': 200})
        alloc, e_ret, e_risk = manager.optimize(
            to_buy=self.buy_signal, to_sell={})
        self._check_optimize_return(alloc, e_ret, e_risk)
        eq_(alloc, {'goog': 200})


class FairManagerTestCase(FactoryManagerTestCase):

    def test_initialize(self):
        self._check_initialization(linear.Fair({}))

    def test_optimize_empty_signals(self):
        manager = linear.Fair({})
        alloc, e_ret, e_risk = manager.optimize({}, {})
        self._check_optimize_return(alloc, e_ret, e_risk)
        eq_(alloc, {})
        eq_(e_ret, 0)
        eq_(e_risk, 1)
