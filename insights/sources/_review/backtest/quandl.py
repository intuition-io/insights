# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Quandl data source
  ------------------

  :copyright (c) 2014 Xavier Bruhiere
  :license: Apache 2.0, see LICENSE for more details.
'''


from intuition.data.quandl import DataQuandl


class QuandlSource(object):
    '''
    Fetchs data from quandl.com
    '''

    def __init__(self):
        # API key must be provided here or store in the environment
        # (QUANDL_API_KEY)
        self.feed = DataQuandl()

    def get_data(self, sids, start, end):

        return self.feed.fetch(sids,
                               start_date=start,
                               end_date=end,
                               returns='pandas')

    @property
    def mapping(self):
        # FIXME Not generic AT ALL
        return {
            'dt': (lambda x: x, 'dt'),
            'sid': (lambda x: x, 'sid'),
            'price': (float, 'Rate'),
            'low': (int, 'Low (est)'),
            'high': (int, 'High (est)'),
            'volume': (lambda x: int(1000 * x), 'Rate'),
            #'price': (float, 'Close'),
            #'volume': (int, 'Volume'),
            #'open': (int, 'Open'),
            #'low': (int, 'Low'),
            #'high': (int, 'High'),
        }
