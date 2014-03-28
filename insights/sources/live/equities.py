# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Insights equities live source
  -----------------------------

  :copyright (c) 2014 Xavier Bruhiere
  :license: Apache 2.0, see LICENSE for more details.
'''

import intuition.data.remote as remote


class Stocks(object):
    '''
    At each event datetime of the provided index, FakeLiveSource
    generates random prices
    '''
    def __init__(self, sids, properties):
        self.feed = remote.Data()

    @property
    def mapping(self):
        return {
            'dt': (lambda x: x, 'dt'),
            'sid': (lambda x: x, 'sid'),
            'price': (float, 'price'),
            'change': (float, 'perc_change'),
            'volume': (lambda x: int(10001), 'price'),
        }

    def get_data(self, sids):
        # FIXME No volumen information with this method
        snapshot = self.feed.fetch_equities_snapshot(
            symbols=sids, level=1)

        if snapshot.empty:
            raise ValueError('no equities data available')
        return snapshot
