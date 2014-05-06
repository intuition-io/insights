'''
Tests for insights.managers.gmv
'''

from nose.tools import eq_, raises, ok_
import insights.managers.gmv as gmv
from insights.test_framework import (
    FactoryManagerTestCase, generate_fake_returns
)


class ComputeWeighsTestCase(FactoryManagerTestCase):
    pass


class GmvManagerTestCase(FactoryManagerTestCase):

    def test_initialize(self):
        manager = gmv.GlobalMinimumVariance()
        self._check_initialization(manager)
        eq_(manager.partial_sell, 1.0)

    def test_optimize_empty_signals(self):
        manager = gmv.GlobalMinimumVariance()
        alloc, e_ret, e_risk = manager.optimize({}, {})
        self._check_optimize_return(alloc, e_ret, e_risk)
        eq_(alloc, {})
        eq_(e_ret, 0)
        eq_(e_risk, 1)

    @raises(NotImplementedError)
    def test_buy_signals_without_returns(self):
        manager = gmv.GlobalMinimumVariance()
        alloc, e_ret, e_risk = manager.optimize({'goog': 45.6}, {})
        self._check_optimize_return(alloc, e_ret, e_risk)

    def test_buy_signals(self):
        manager = gmv.GlobalMinimumVariance()
        manager.advise(historical_prices=generate_fake_returns(self.test_sids))
        alloc, _, _ = manager.optimize({'goog': 45.6}, {})
        ok_(alloc)
        for sid, weigh in alloc.iteritems():
            self.assertIsInstance(alloc[sid], float)
            self.assertGreaterEqual(weigh, 0)
            self.assertLessEqual(weigh, 1)
            self.assertIn(sid, self.test_sids)

    def test_default_sell_signals(self):
        to_sell = self.test_sids[0]
        manager = gmv.GlobalMinimumVariance()
        manager.update(self.test_pf, None, None)
        eq_(manager.portfolio, self.test_pf)
        alloc, _, _ = manager.optimize({}, [to_sell])
        eq_(alloc[to_sell], - self.test_pf.positions[to_sell].amount)
