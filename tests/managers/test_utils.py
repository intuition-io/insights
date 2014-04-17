'''
Tests for insights.managers.utils
'''

import unittest
from nose.tools import eq_
from random import random
import numpy as np
import insights.managers.utils as utils


class ManagerUtilsTestCase(unittest.TestCase):

    def test_simplex_projection(self):
        vector = [random() for _ in range(4)]
        proj = utils.simplex_projection(vector)
        self.assertIsInstance(proj, np.ndarray)
        eq_(len(vector), len(proj))
        self.assertAlmostEqual(proj.sum(), 1.0)
        eq_(filter(lambda x: x < 0, proj), [])
