# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Backtest data source fetching from yahoo finance
  ------------------------------------------------

  :copyright (c) 2014 Xavier Bruhiere
  :license: Apache 2.0, see LICENSE for more details.
'''

import intuition.data.remote as remote


class YahooPrices(object):
    '''
    doc: Fetchs prices for the given sids from yahoo.com
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

    def get_data(self, sids, start, end):
        return remote.Data().fetch_equities_daily(
            sids, indexes={}, start=start, end=end)


class YahooOHLC(object):
    '''
    doc: Fetchs OHLC data for the given sids from yahoo.com
    '''

    def __init__(self, sids, properties):
        pass

    @property
    def mapping(self):
        return {
            'dt': (lambda x: x, 'dt'),
            'sid': (lambda x: x, 'sid'),
            'price': (float, 'price'),
            'open': (float, 'open'),
            'high': (float, 'high'),
            'close': (float, 'close'),
            'low': (float, 'low'),
            'volume': (int, 'volume'),
        }

    def get_data(self, sids, start, end):
        data = remote.Data().fetch_equities_daily(
            sids, ohlc=True, indexes={}, start=start, end=end)
        #import ipdb; ipdb.set_trace()
        self.sids = data.items
        return data
