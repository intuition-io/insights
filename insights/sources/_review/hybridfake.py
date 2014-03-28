# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Hybrid data source prototype
  ----------------------------

  Combine a live random source with a backtest database to provide a data
  source working from the past to the future !

  :copyright (c) 2014 Xavier Bruhiere
  :license: Apache 2.0, see LICENSE for more details.
'''

from insights.sources.backtest.database import RethinkdbPrices
from insights.sources.live.fake import FakeLiveSource
from intuition.api.data_source import HybridDataFactory


def clean_name(sid):
    # Remove forex forbidden character
    sid = sid.replace('/', '')
    # Remove market related extension
    dot_pos = sid.find('.')
    return sid[:dot_pos] if dot_pos > 0 else sid


class RandomPrices(HybridDataFactory):
    ''' Get quotes from Rethinkdb database for backtest,  and generate random
    ones for live trading '''

    def initialize(self, data_descriptor, **kwargs):
        self.backtest = RethinkdbPrices(data_descriptor)
        self.live = FakeLiveSource()

        if self.sids[0] == 'random':
            # --universe random[,4]
            count = int(self.sids[1]) if (len(self.sids) == 2) else 10
            self.sids = self.backtest.db.random_tables(count)
        else:
            self.sids = map(clean_name, self.sids)

    def backtest_data(self):
        data = self.backtest.get_data(
            self.sids, self.start, self.end, select='rate')
        # Unknown data were poped from dataframe
        self.sids = data.columns
        return data

    def live_data(self):
        return self.live.get_data(self.sids)
