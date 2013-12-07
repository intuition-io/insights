#
# Copyright 2013 Xavier Bruhiere
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import time
import logbook
import pandas as pd

from intuition.zipline.data_source import DataFactory
from intuition.data.forex import ConnectTrueFX


log = logbook.Logger('intuition.sources.live.forex')


class ForexLiveSource(DataFactory):
    """
    At each event datetime of the provided index, ForexLiveSource fetchs live
    forex data from TrueFX.
    Supported universe is as follow
    EUR/USD  USD/JPY  GBP/USD  EUR/GBP  USD/CHF  EUR/JPY  EUR/CHF  USD/CAD
    AUD/USD  GBP/JPY  AUD/JPY  AUD/NZD  CAD/JPY  CHF/JPY  NZD/USD
    """
    @property
    def mapping(self):
        return {
            'dt': (lambda x: x, 'dt'),
            #TODO Here conversion (weird result for now)
            # Or: (lambda x: pd.tslib.i8_to_pydt(x + '000000'), 'trade_time'),
            'trade_time': (lambda x: pd.datetime.utcfromtimestamp(
                float(x[:-3])), 'trade_time'),
            'sid': (lambda x: x, 'sid'),
            'price': (float, 'bid'),
            'ask': (float, 'ask'),
            'high': (float, 'high'),
            'low': (float, 'low'),
            'volume': (int, 'volume')
        }

    def get_data(self):
        while True:
            rates = self.forex.QueryTrueFX()
            if len(rates.keys()) >= len(self.sids):
                log.info('New income data, fire an event !')
                log.debug('Data available:\n{}'.format(rates))
                break
            log.debug('Waiting for Forex update')
            time.sleep(30)
        return rates

    def raw_data_gen(self):
        self.forex = ConnectTrueFX(pairs=self.sids)
        index = self._get_updated_index()
        import ipdb; ipdb.set_trace()
        for dt in index:
            self._wait_for_dt(dt)
            rates = self.get_data()

            for sid in self.sids:
                assert sid in rates.columns
                event = self.build_event(dt, sid, rates)
                '''
                event = {
                    'dt': dt,
                    'sid': sid,
                    'trade_time': rates[sid]['TimeStamp'],
                    'bid': rates[sid]['Bid.Price'],
                    'ask': rates[sid]['Ask.Price'],
                    'high': rates[sid]['High'],
                    'low': rates[sid]['Low'],
                    'volume': 10000
                }
                '''
                yield event
