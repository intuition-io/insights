'''
Tests for insights.plugins.utils
'''

import unittest
from dna.logging import logger
import insights.plugins.utils as utils


class FakeCumulativeRisks(object):
    def to_dict(self):
        return {'what': 'ever'}


class FakePerfs(object):
    def __init__(self, progress=0.0):
        self.progress = progress
        self.cumulative_risk_metrics = FakeCumulativeRisks()


class PluginsUtilsTestCase(unittest.TestCase):

    def test_debug_portfolio(self):
        self.assertIsNone(utils.debug_portfolio(
            logger(__name__), '2012/01/01', None))

    def test_debug_intial_metrics(self):
        self.assertIsNone(utils.debug_metrics(
            logger(__name__), '2012/01/01', FakePerfs()))

    def test_debug_metrics(self):
        self.assertIsNone(utils.debug_metrics(
            logger(__name__), '2012/01/01', FakePerfs(0.3)))
