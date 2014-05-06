'''
Tests for insights.algorithms.dummy
'''

from nose.tools import ok_, eq_
from insights.test_framework import FactoryAlgorithmTestCase
import insights.algorithms.dummy as dummy


class RandomAlgoTestCase(FactoryAlgorithmTestCase):

    def test_doc(self):
        self._check_yaml_doc(dummy.Random)

    def test_initialize_default(self):
        algo = dummy.Random()
        eq_(algo.identity, self.default_identity)
        eq_(algo.middlewares, [])
        ok_(algo.buy_trigger > 0.5 and algo.buy_trigger < 1)
        ok_(algo.sell_trigger > 0 and algo.sell_trigger < 0.5)

    def test_initialize_custom_signal_triggers(self):
        algo = dummy.Random(properties={
            'buy_trigger': 0.6,
            'sell_trigger': 0.3,
        })
        eq_(algo.buy_trigger, 0.6)
        eq_(algo.sell_trigger, 0.3)

    def test_initialize_custom_middlewares(self):
        algo = dummy.Random(properties={
            'mobile': 'Nexus 5',
            'interactive': True
        })
        eq_(len(algo.middlewares), 2)

    def test_event_output(self):
        algo = dummy.Random()
        self._check_event_output(algo.event(self.event_data))

    def test_deactivate_buy_and_sell(self):
        algo = dummy.Random(properties={
            'buy_trigger': 10.0,
            'sell_trigger': -10.0
        })
        signals = algo.event(self.event_data)
        eq_(signals['buy'], {})
        eq_(signals['sell'], {})

    def test_always_buy_and_cannot_sell(self):
        algo = dummy.Random(properties={
            'buy_trigger': -10.0,
            'sell_trigger': 10.0
        })
        signals = algo.event(self.event_data)
        ok_(signals['buy'])
        eq_(signals['sell'], {})

    def test_always_sell_and_cannot_buy(self):
        algo = dummy.Random(properties={
            'buy_trigger': 10.0,
            'sell_trigger': 10.0
        })
        signals = algo.event(self.event_data)
        ok_(signals['sell'])
        eq_(signals['buy'], {})
