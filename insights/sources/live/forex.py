# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Insights Forex live source
  --------------------------

  :copyright (c) 2014 Xavier Bruhiere
  :license: Apache 2.0, see LICENSE for more details.
'''


import time
import pandas as pd
import dna.logging
from intuition.data.forex import ConnectTrueFX


log = dna.logging.logger(__name__)


class ForexLiveSource(object):
    '''
    At each event datetime of the provided index, ForexLiveSource fetchs live
    forex data from TrueFX.
    Supported universe is as follow
    EUR/USD  USD/JPY  GBP/USD  EUR/GBP  USD/CHF  EUR/JPY  EUR/CHF  USD/CAD
    AUD/USD  GBP/JPY  AUD/JPY  AUD/NZD  CAD/JPY  CHF/JPY  NZD/USD
    '''
    def __init__(self, pairs):
        self.forex = ConnectTrueFX(pairs=pairs)

    @property
    def mapping(self):
        return {
            'dt': (lambda x: x, 'dt'),
            #TODO Here conversion (weird result for now)
            # Or: (lambda x: pd.tslib.i8_to_pydt(x + '000000'), 'trade_time'),
            'trade_time': (lambda x: pd.datetime.utcfromtimestamp(
                float(x[:-3])), 'TimeStamp'),
            'sid': (lambda x: x, 'sid'),
            'price': (float, 'Bid.Price'),
            'ask': (float, 'Ask.Price'),
            'high': (float, 'High'),
            'low': (float, 'Low'),
            'volume': (int, 'volume')
        }

    def get_data(self, sids):
        while True:
            rates = self.forex.query_trueFX()
            if len(rates.keys()) >= len(sids):
                log.info('New income data, fire an event !')
                log.debug('Data available:\n{}'.format(rates))
                break
            log.debug('Waiting for Forex update')
            time.sleep(30)
        #FIXME We need volume field to be consistent with the API
        return rates.append(pd.DataFrame(
            {sid: {'volume': 1000} for sid in rates.columns}))
