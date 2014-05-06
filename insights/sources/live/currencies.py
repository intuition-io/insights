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
import intuition.data.forex as forex

log = dna.logging.logger(__name__)


class Forex(object):
    '''
    At each event datetime of the provided index, ForexLiveSource fetchs live
    forex data from TrueFX.
    '''

    def __init__(self, pairs, properties):
        self._wait_retry = properties.get('retry', 10)
        self.forex = forex.TrueFX(pairs=pairs)
        self.forex.connect()

    def get_data(self, sids):
        while True:
            rates = self.forex.query_rates()
            if len(rates.keys()) >= len(sids):
                log.debug('Data available for {}'.format(rates.keys()))
                break
            log.debug('Incomplete data ({}/{}), retrying in {}s'.format(
                len(rates.keys()), len(sids), self._wait_retry))
            time.sleep(self._wait_retry)
            debug_feedback = self.forex.connect()
            log.info('New Truefx connection: {}'.format(debug_feedback))

        return rates

    @property
    def mapping(self):
        return {
            'dt': (lambda x: x, 'dt'),
            #TODO Here conversion (weird result for now)
            # Or: (lambda x: pd.tslib.i8_to_pydt(x + '000000'), 'trade_time'),
            'trade_time': (lambda x: pd.datetime.utcfromtimestamp(
                float(x[:-3])), 'timeStamp'),
            'sid': (lambda x: x, 'sid'),
            'price': (float, 'bid'),
            'ask': (float, 'ask'),
            'high': (float, 'high'),
            'low': (float, 'low'),
            'volume': (lambda x: 10000, 'bid')
        }
