'''
Tests for insights.contexts.file
'''

import unittest
from nose.tools import ok_, eq_, raises, nottest
import os
import yaml
import json
import insights.contexts.file as context


class FileContextTestCase(unittest.TestCase):

    def setUp(self):
        self.supported_file_types = [('json', json),
                                     ('yml', yaml),
                                     ('yaml', yaml)]
        self.file_special_intuition = 'localhost/intuition/test.yml'
        self.file_bad_type = 'localhost/intuition/test.nothing'
        self.file_bad_path = 'localhost/nowhere/test.yml'
        self.right_yaml_file = 'localhost/contexts/_config/backtest.yml'
        self.right_json_file = 'localhost/contexts/_config/live.json'

    def test_initialize(self):
        loader = context.FileContext('localhost/_config/test.yml')
        ok_(hasattr(loader, 'log'))
        eq_(loader.configfile, '_config/test.yml')

    def test_intuition_special_path(self):
        loader = context.FileContext(self.file_special_intuition)
        expected_path = os.path.expanduser('~/.intuition/test.yml')
        eq_(loader.configfile, expected_path)

    def test_file_supports(self):
        for extension, module in self.supported_file_types:
            loader = context.FileContext('localhost/_config/test.' + extension)
            eq_(loader.fmt_module, module)

    @raises(NotImplementedError)
    def test_wrong_file_type(self):
        context.FileContext(self.file_bad_type)

    @raises(ValueError)
    def test_load_absent_file(self):
        loader = context.FileContext(self.file_bad_path)
        loader.load()

    @nottest
    def _check_config(self, config):
        self.assertIsInstance(config, dict)
        self.assertIsInstance(config['modules'], dict)
        self.assertIn('universe', config)
        self.assertIn('algorithm', config['modules'])

    def test_load_yaml_config(self):
        loader = context.FileContext(self.right_yaml_file)
        self._check_config(loader.load())

    def test_load_json_config(self):
        loader = context.FileContext(self.right_json_file)
        self._check_config(loader.load())
