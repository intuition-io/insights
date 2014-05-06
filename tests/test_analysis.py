'''
Tests for insights.analysis
'''

import unittest
from nose.tools import eq_, ok_
import rpy2
import os
from dna.test_utils import setup_logger, teardown_logger
import insights.analysis as analysis


class StocksAnalysisTestCase(unittest.TestCase):

    def setUp(self):
        setup_logger(self)
        self.default_template_path = os.path.expanduser(
            '~/.intuition/assets/report.rnw')

    def tearDown(self):
        teardown_logger(self)

    def test_default_intialize(self):
        analyzer = analysis.Stocks()
        eq_(analyzer.report_template,
            self.default_template_path)
        eq_(analyzer.report_template,
            os.path.expanduser(analyzer.knitr_report))
        self.assertIsInstance(analyzer.r, rpy2.robjects.R)

    def test_custom_intialize(self):
        analyzer = analysis.Stocks(report_template='here.rnw')
        eq_(analyzer.report_template, 'here.rnw')

    def test_cleanup_garbage_when_nothing(self):
        analyzer = analysis.Stocks()
        self.assertIsNone(analyzer.clean())

    # TODO Test figure directory
    def test_cleanup_garbage(self):
        analyzer = analysis.Stocks()
        os.system('touch report.aux')
        self.assertIsNone(analyzer.clean())
        ok_(not os.path.exists('report.aux'))

    def test_cleanup_everything(self):
        analyzer = analysis.Stocks()
        os.system('touch report.pdf')
        self.assertIsNone(analyzer.clean())
        ok_(os.path.exists('report.pdf'))
        self.assertIsNone(analyzer.clean(everything=True))
        ok_(not os.path.exists('report.pdf'))
