# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Insights fake live source
  -------------------------

  :copyright (c) 2014 Xavier Bruhiere
  :license: Apache 2.0, see LICENSE for more details.
'''

import random
import pandas as pd


class Random(object):
    '''
    At each event datetime of the provided index, FakeLiveSource
    generates random prices
    '''
    def __init__(self, sids, properties):
        pass

    @property
    def mapping(self):
        return {
            'dt': (lambda x: x, 'dt'),
            'sid': (lambda x: x, 'sid'),
            'price': (float, 'price'),
            'volume': (int, 'volume'),
        }

    def _feed_random_data(self):
        return {
            'price': 100 * random.random(),
            'volume': random.randrange(1000, 10000)
        }

    def get_data(self, sids):
        data = {}
        for sid in sids:
            data[sid] = self._feed_random_data()

        return pd.DataFrame(data)
