# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Hybrid data source, trading forex
  ---------------------------------

  :copyright (c) 2014 Xavier Bruhiere
  :license: Apache 2.0, see LICENSE for more details.
'''

from insights.sources.live.forex import ForexLiveSource
from intuition.api.data_source import HybridDataFactory


class ForexPrices(HybridDataFactory):
    ''' Get quotes from database for backtest, and from TrueFX.com for live
    trading '''

    def initialize(self, data_descriptor, **kwargs):
        if self.sids[0] == 'random':
            # --universe random[,4]
            count = int(self.sids[1]) if (len(self.sids) == 2) else 10
            self.sids = self.db.random_tables(count)

        self.live = ForexLiveSource(self.sids)

    def backtest_data(self):
        raise NotImplementedError(
            'no backtest support for {}'.format(__name__))

    def live_data(self):
        return self.live.get_data(self.sids)
