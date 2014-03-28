# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Hybrid data source, trading forex
  ---------------------------------

  :copyright (c) 2014 Xavier Bruhiere
  :license: Apache 2.0, see LICENSE for more details.
'''

from insights.sources.backtest.database import RethinkdbPrices
from insights.sources.live.forex import ForexLiveSource
from intuition.api.data_source import HybridDataFactory


def clean_name(sid):
    # Remove forex forbidden character
    sid = sid.replace('/', '').lower()
    # Remove market related extension
    dot_pos = sid.find('.')
    return sid[:dot_pos] if dot_pos > 0 else sid


class ForexRates(HybridDataFactory):
    ''' Get quotes from database for backtest, and from TrueFX.com for live
    trading '''

    def initialize(self, data_descriptor, **kwargs):
        self.backtest = RethinkdbPrices(data_descriptor)
        self.live = ForexLiveSource(self.sids)

        if self.sids[0] == 'random':
            # --universe random[,4]
            count = int(self.sids[1]) if (len(self.sids) == 2) else 10
            self.sids = self.db.random_tables(count)
        else:
            self.sids = map(clean_name, self.sids)

    def backtest_data(self):
        data = self.backtest.get_data(
            self.sids, self.start, self.end, select='rate')
        # Unknown data were poped from dataframe
        self.sids = data.columns
        return data

    def live_data(self):
        data = self.live.get_data(self.sids)
        data.columns = map(clean_name, data.columns)
        return data
