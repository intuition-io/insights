# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Backtest data source using database
  -----------------------------------

  :copyright (c) 2014 Xavier Bruhiere
  :license: Apache 2.0, see LICENSE for more details.
'''

import pandas as pd
import copy
from insights.plugins.database.rethink import RethinkdbFinance
from intuition.data.quandl import DataQuandl


# NOTE It would be cool if this class could inherit from the one above
class RethinkdbBackedByQuandl(object):
    '''
    doc: Fetch quotes from a <a href="http://rethinkdb.com/">Rethinkdb</a>
      database. If not found, it will try to download it from <a
      href="http://quandl.com">Quandl</a>.
    parameters:
      db: Database name [default quotes],
      select: field to considere, like open, rate, ... [default All]
      save_missing: Wether save or not in database the data downloaded
        [default false]
      offline: Wether to allow or not missing data downloading [default false]
    '''

    def __init__(self, sids, properties):
        ''' Combine rethinkdb and quandl backends '''
        # Should save dataframes downloaded from quandl ?
        self._save_missing_data = properties.get('save_missing')
        # Allow downloads ?
        self._offline = properties.get('offline')
        # Only get from db or quandl this field
        select = properties.get('select')
        self._select = [select] if select else []

        self.db = RethinkdbFinance(db=properties.get('db', 'quotes'))
        self.quandl = DataQuandl()

        # TODO Check with dates
        self._missing_sids = [sid for sid in sids
                              if not self.db.available(sid)]

        # Select the right mapping
        if self._select:
            self.mapping_choice = 'whatever_dataframe'
        else:
            if properties['universe'].exchange == 'forex':
                self.mapping_choice = 'forex_panel'
            else:
                #if properties['universe'].exchange.find('paris') > 0:
                self.mapping_choice = 'stock_panel'

    def _dl_missing_data(self, data, start, end):
        missing_data = self.quandl.fetch(
            self._missing_sids, start=start, end=end)
        # FIXME Handle symbols not found
        for sid, series in missing_data.iteritems():
            if self._select:
                if data.empty:
                    data = pd.DataFrame(
                        series[self._select], index=missing_data[sid].index)
                else:
                    data[sid] = series[self._select]
            else:
                if data.empty:
                    data = pd.Panel({sid: series})
                else:
                    data[sid] = series
            if self._save_missing_data:
                self.db.save_quotes(
                    sid, series, {}, reset=True)

        return data

    def get_data(self, sids, start, end):
        data = self.db.quotes(
            sids, start=start, end=end, select=copy.copy(self._select))

        if self._missing_sids and not self._offline:
            data = self._dl_missing_data(data, start, end)

        return data.fillna(method='pad')

    @property
    def mapping(self):
        mapping = {
            'forex_panel': {
                'dt': (lambda x: x, 'dt'),
                'sid': (lambda x: x, 'sid'),
                'price': (lambda x: x, 'rate'),
                'low': (lambda x: x, 'low_(est)'),
                'high': (lambda x: x, 'high_(est)'),
                'volume': (lambda x: 100001, 'rate')
            },
            'stock_panel': {
                'dt': (lambda x: x, 'dt'),
                'sid': (lambda x: x, 'sid'),
                'price': (lambda x: x, 'adjusted_close'),
                'open': (lambda x: x, 'open'),
                'low': (lambda x: x, 'low'),
                'high': (lambda x: x, 'high'),
                'close': (lambda x: x, 'close'),
                'volume': (lambda x: x, 'volume')
            },
            'whatever_dataframe': {
                'dt': (lambda x: x, 'dt'),
                'sid': (lambda x: x, 'sid'),
                'price': (lambda x: x, 'price'),
                'volume': (lambda x: 100001, 'price')
            }
        }
        return mapping[self.mapping_choice]
