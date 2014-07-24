'''
Tests for insights.algorithms.utils
'''

import unittest
from nose.tools import eq_, ok_
import inspect
import insights.algorithms.utils as utils


class AlgorithmsUtilsTestCase(unittest.TestCase):

    def test_empty_common_middlewares(self):
        nothing_required = {}
        middlewares = utils.common_middlewares(nothing_required, 'whatever')
        eq_(middlewares, [])

    def test_full_common_middlewares(self):
        # TODO For simplicity, rethinkdb is excluded for now
        full_required = {
            'orders': 'on',
            'save': False,
            'interactive': True,
            'mobile': 'Nexus 5',
            'hipchat': '123456'
        }
        middlewares = utils.common_middlewares(full_required, 'whatever')
        eq_(len(middlewares), 4)
        for middleware in middlewares:
            ok_(inspect.ismethod(middleware['func']))
            self.assertIsInstance(middleware['backtest'], bool)
