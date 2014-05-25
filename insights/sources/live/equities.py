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
    Download live (or slightly delayed) quotes from Google Finance
    '''

    _specific_mapping = {
        'google': {
            'price': (float, 'price'),
            'change': (float, 'perc_change'),
            'volume': (lambda x: int(10001), 'price')
        },
        # NOTE short_ration also available but often returned as NaN
        'yahoo': {
            'price': (float, 'last'),
            # NOTE Often to N/A outside US
            # 'change': (float, 'change_pct'),
            # 'pe': (float, 'PE'),
            'volume': (lambda x: int(10001), 'last')
        }
    }

    def __init__(self, sids, properties):
        self._source = properties.get('source', 'yahoo')
        self._mapping = {
            'dt': (lambda x: x, 'dt'),
            'sid': (lambda x: x, 'sid'),
        }
        if self._source in self._specific_mapping.keys():
            self._mapping.update(self._specific_mapping[self._source])
        else:
            raise ValueError('{} source not available.'.format(self._source))

    @property
    def mapping(self):
        return self._mapping

    def get_data(self, sids):
        # FIXME No volume information with this method
        if self._source == 'google':
            snapshot = remote.snapshot_google(symbols=sids)
        elif self._source == 'yahoo':
            snapshot = remote.snapshot_yahoo_pandas(symbols=sids)

        if snapshot.empty:
            raise ValueError('no equities data available')
        return snapshot
