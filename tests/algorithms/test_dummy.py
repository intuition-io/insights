'''
Tests for insights.algorithms.dummy
'''

from nose.tools import ok_, eq_
import yaml
import copy
from insights.test_framework import FactoryAlgorithmTestCase
import insights.algorithms.dummy as dummy


class RandomALgoTestCase(FactoryAlgorithmTestCase):

    def test_yaml_doc(self):
        doc = yaml.load(dummy.Random.__doc__)
        ok_(isinstance(doc, dict))
        self.assertIn('doc', doc)
        ok_(isinstance(doc.get('parameters', {}), dict))

    def test_initialize_default(self):
        Algo = copy.deepcopy(dummy.Random)
        Algo.identity = 'test_random'
        algo = Algo(properties={})
        eq_(algo.identity, 'test_random')
        eq_(algo.middlewares, [])
        ok_(algo.buy_trigger > 0.5 and algo.buy_trigger < 1)
        ok_(algo.sell_trigger > 0 and algo.sell_trigger < 0.5)

    '''
    # FIXME Algo is shared between tests
    def test_initialize_custom(self):
        Algo = copy.deepcopy(dummy.Random)
        Algo.identity = 'test_random'
        algo = Algo(properties={
            'buy_trigger': 0.6,
            'sell_trigger': 0.3,
            'hipchat': '12346',
            'mobile': 'Nexus 5',
            'interactive': True
        })
        eq_(algo.identity, 'test_random')
        eq_(len(algo.middlewares), 3)
        eq_(algo.buy_trigger, 0.6)
        eq_(algo.sell_trigger, 0.3)
    '''
