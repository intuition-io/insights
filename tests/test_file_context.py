'''
Tests for intuition.core.configuration
'''

import unittest
import insights.contexts.file as context


class FileContextTestCase(unittest.TestCase):

    def test_fail_file_context_load(self):
        conf, strategy = context.build_context('notexists.yml')
        self.assertTrue('algorithm' in strategy and 'manager' in strategy)
        self.assertFalse(conf)
        self.assertFalse(strategy['algorithm'])
        self.assertFalse(strategy['manager'])
